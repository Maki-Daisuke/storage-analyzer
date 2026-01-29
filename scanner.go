package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"sync"

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
	concurrency := int64(4)
	if env := os.Getenv("SCAN_CONCURRENCY"); env != "" {
		if val, err := strconv.Atoi(env); err == nil && val > 0 {
			concurrency = int64(val)
		}
	}
	sem = semaphore.NewWeighted(concurrency)
}

func ScanFolder(path string) (*FileNode, error) {
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
		node.Size = info.Size()
		node.FileCount = 1
		return node, nil
	}

	entries, err := os.ReadDir(path)
	if err != nil {
		node.Error = fmt.Sprintf("Access denied: %v", err)
		return node, nil
	}

	var mu sync.Mutex
	var wg sync.WaitGroup

	children := make([]*FileNode, len(entries)) // Pre-allocate with correct size

	for i, entry := range entries {
		childPath := filepath.Join(path, entry.Name())

		if !entry.IsDir() {
			// Fast path for files
			info, err := entry.Info()
			size := int64(0)
			if err == nil {
				size = info.Size()
			}
			children[i] = &FileNode{
				Name:      entry.Name(),
				Path:      childPath,
				Type:      "file",
				Size:      size,
				FileCount: 1,
			}
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

				childNode, err := ScanFolder(cPath)
				if err != nil {
					childNode = &FileNode{
						Name:  name,
						Path:  cPath,
						Type:  "directory",
						Error: fmt.Sprintf("Scan error: %v", err),
					}
				}
				mu.Lock()
				children[idx] = childNode
				mu.Unlock()
			}(i, childPath, entry.Name())
		} else {
			// Buffer full, run synchronously
			func(idx int, cPath string, name string) {
				defer wg.Done()
				childNode, err := ScanFolder(cPath)
				if err != nil {
					childNode = &FileNode{
						Name:  name,
						Path:  cPath,
						Type:  "directory",
						Error: fmt.Sprintf("Scan error: %v", err),
					}
				}
				mu.Lock()
				children[idx] = childNode
				mu.Unlock()
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
