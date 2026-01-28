package main

import (
	"context"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App struct
type App struct {
	ctx context.Context
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// Scan performs a recursive scan of the given directory
func (a *App) Scan(path string) ScanResult {
	node, err := ScanFolder(path)
	if err != nil {
		return ScanResult{Error: err.Error()}
	}
	return ScanResult{Root: node}
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
