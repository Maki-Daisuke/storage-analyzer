package main

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"sync"
	"sync/atomic"

	"golang.org/x/sync/semaphore"
)

// FileNode represents a file or directory in the storage tree
type FileNode struct {
	Name      string      `json:"name"`
	Path      string      `json:"path"`
	Size      int64       `json:"size"`
	FileCount int         `json:"fileCount"`
	Type      string      `json:"type"` // "directory" or "file"
	Children  []*FileNode `json:"children,omitempty"`
	Error     string      `json:"error,omitempty"`
}

// ScanResult contains the result of a scan operation
type ScanResult struct {
	Root  *FileNode `json:"root"`
	Error string    `json:"error,omitempty"`
}

var sem *semaphore.Weighted

func init() {
	concurrency := int64(runtime.NumCPU() / 2) // Default is half of CPU cores
	if env := os.Getenv("SCAN_CONCURRENCY"); env != "" {
		if val, err := strconv.Atoi(env); err == nil && val > 0 {
			concurrency = int64(val)
		}
	}
	sem = semaphore.NewWeighted(concurrency)
}

// Scanner handles file system scanning
type Scanner struct {
	totalFiles      int64
	onProgress      func(int64)
	usePhysicalSize bool
}

// NewScanner creates a new Scanner instance
func NewScanner(onProgress func(int64), usePhysicalSize bool) *Scanner {
	return &Scanner{
		onProgress:      onProgress,
		usePhysicalSize: usePhysicalSize,
	}
}

// Scan scans the given directory
func (s *Scanner) Scan(path string) (*FileNode, error) {
	// Reset counter
	atomic.StoreInt64(&s.totalFiles, 0)
	return s.scanRecursive(path)
}

func (s *Scanner) scanRecursive(path string) (*FileNode, error) {
	info, err := os.Stat(path)
	if err != nil {
		return nil, err
	}

	node := &FileNode{
		Name: info.Name(),
		Path: path,
		Type: "directory",
	}

	if !info.IsDir() {
		node.Type = "file"
		if s.usePhysicalSize {
			node.Size = getPhysicalSize(path, info)
		} else {
			node.Size = info.Size()
		}
		node.FileCount = 1
		s.incrementProgress()
		return node, nil
	}

	entries, err := os.ReadDir(path)
	if err != nil {
		node.Error = fmt.Sprintf("Access denied: %v", err)
		return node, nil
	}

	var wg sync.WaitGroup

	children := make([]*FileNode, len(entries)) // Pre-allocate with correct size

	for i, entry := range entries {
		childPath := filepath.Join(path, entry.Name())

		// Check if it is a Symlink or Reparse Point (Junction)
		// even if IsDir() is true. If so, treat as file to avoid infinite recursion.
		if isSymLink(entry) {
			children[i] = &FileNode{
				Name:      entry.Name(),
				Path:      childPath,
				Type:      "file", // Treat as file (leaf)
				Size:      0,      // Symlink size is negligible or pointer size
				FileCount: 1,
			}
			s.incrementProgress()
			continue
		}

		if !entry.IsDir() {
			// Fast path for regular files
			info, err := entry.Info()
			size := int64(0)
			if err == nil {
				if s.usePhysicalSize {
					size = getPhysicalSize(childPath, info)
				} else {
					size = info.Size()
				}
			}
			children[i] = &FileNode{
				Name:      entry.Name(),
				Path:      childPath,
				Type:      "file",
				Size:      size,
				FileCount: 1,
			}
			s.incrementProgress()
			continue
		}

		// It's a directory, try to parallelize
		wg.Add(1)

		// "Greedy with fallback" strategy to prevent deadlock
		if sem.TryAcquire(1) {
			// We acquired a token, run in goroutine
			go func(idx int, cPath string, name string) {
				defer wg.Done()
				defer sem.Release(1) // Release token

				childNode, err := s.scanRecursive(cPath)
				if err != nil {
					childNode = &FileNode{
						Name:  name,
						Path:  cPath,
						Type:  "directory",
						Error: fmt.Sprintf("Scan error: %v", err),
					}
				}
				// Safe to assign directly as each goroutine uses a unique index
				children[idx] = childNode
			}(i, childPath, entry.Name())
		} else {
			// Buffer full, run synchronously
			func(idx int, cPath string, name string) {
				defer wg.Done()
				childNode, err := s.scanRecursive(cPath)
				if err != nil {
					childNode = &FileNode{
						Name:  name,
						Path:  cPath,
						Type:  "directory",
						Error: fmt.Sprintf("Scan error: %v", err),
					}
				}
				// Safe to assign directly as each goroutine uses a unique index
				children[idx] = childNode
			}(i, childPath, entry.Name())
		}
	}

	wg.Wait()

	var totalSize int64
	var totalFiles int

	finalChildren := make([]*FileNode, 0, len(entries))
	for _, child := range children {
		if child != nil {
			totalSize += child.Size
			totalFiles += child.FileCount
			finalChildren = append(finalChildren, child)
		}
	}

	node.Size = totalSize
	node.FileCount = totalFiles
	node.Children = finalChildren

	return node, nil
}

func (s *Scanner) incrementProgress() {
	count := atomic.AddInt64(&s.totalFiles, 1)
	if s.onProgress != nil && count%100 == 0 { // Call callback every 100 files
		s.onProgress(count)
	}
}
