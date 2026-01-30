package main

import (
	"context"
	"sync"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App struct
type App struct {
	ctx        context.Context
	nodeCache  map[string]*FileNode
	cacheMutex sync.RWMutex
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{
		nodeCache: make(map[string]*FileNode),
	}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// Scan performs a recursive scan of the given directory
func (a *App) Scan(path string) ScanResult {
	onProgress := func(count int64) {
		runtime.EventsEmit(a.ctx, "scan:progress", count)
	}

	scanner := NewScanner(onProgress)
	node, err := scanner.Scan(path)
	if err != nil {
		return ScanResult{Error: err.Error()}
	}

	// Cache the nodes for lazy loading
	a.cacheMutex.Lock()
	a.nodeCache = make(map[string]*FileNode)
	a.addToCache(node)
	a.cacheMutex.Unlock()

	// Return pruned tree (depth 1)
	return ScanResult{Root: a.pruneTree(node, 1)}
}

// GetSubdirectory returns the children of a specific path from the cache
func (a *App) GetSubdirectory(path string) []*FileNode {
	a.cacheMutex.RLock()
	defer a.cacheMutex.RUnlock()

	if node, exists := a.nodeCache[path]; exists {
		// Return children pruned to depth 1 (i.e., immediate children only, no grandchildren)
		// We need to return a slice of copies where each child has nil Children
		
		result := make([]*FileNode, len(node.Children))
		for i, child := range node.Children {
			// Create a shallow copy for the response
			childCopy := *child
			childCopy.Children = nil // Strip grandchildren
			result[i] = &childCopy
		}
		return result
	}
	return nil
}

// addToCache recursively adds nodes to the map
func (a *App) addToCache(node *FileNode) {
	if node == nil {
		return
	}
	a.nodeCache[node.Path] = node
	for _, child := range node.Children {
		a.addToCache(child)
	}
}

// pruneTree creates a copy of the tree up to the specified depth
func (a *App) pruneTree(node *FileNode, depth int) *FileNode {
	if node == nil {
		return nil
	}

	// Shallow copy
	newNode := *node
	
	if depth <= 0 {
		newNode.Children = nil
		return &newNode
	}

	if node.Children != nil {
		newNode.Children = make([]*FileNode, len(node.Children))
		for i, child := range node.Children {
			newNode.Children[i] = a.pruneTree(child, depth-1)
		}
	}

	return &newNode
}

// SelectFolder opens a dialog to select a folder
func (a *App) SelectFolder() string {
	selection, err := runtime.OpenDirectoryDialog(a.ctx, runtime.OpenDialogOptions{
		Title: "Select Folder to Analyze",
	})
	if err != nil {
		return ""
	}
	return selection
}
