package main

import (
	"fmt"
	"os"
	"path/filepath"
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

// Global variable to stop scanning if needed (optional implementation)
// var stopScanning bool

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
		// Even if we can't read dir, we return the node as is
		return node, nil
	}

	var totalSize int64
	var totalFiles int
	children := make([]*FileNode, 0, len(entries))

	for _, entry := range entries {
		childPath := filepath.Join(path, entry.Name())
		var childNode *FileNode

		if entry.IsDir() {
			childNode, err = ScanFolder(childPath)
			if err != nil {
				// Should guard against individual folder failures breaking the whole scan?
				// For now, we note the error in the child node or skip
				// If ScanFolder returns error for stat failure, we handle it
				childNode = &FileNode{
					Name:  entry.Name(),
					Path:  childPath,
					Type:  "directory",
					Error: fmt.Sprintf("Scan error: %v", err),
				}
			}
		} else {
			info, err := entry.Info()
			size := int64(0)
			if err == nil {
				size = info.Size()
			}
			childNode = &FileNode{
				Name:      entry.Name(),
				Path:      childPath,
				Type:      "file",
				Size:      size,
				FileCount: 1,
			}
		}
		
		totalSize += childNode.Size
		totalFiles += childNode.FileCount
		children = append(children, childNode)
	}

	node.Size = totalSize
	node.FileCount = totalFiles
	node.Children = children

	return node, nil
}
