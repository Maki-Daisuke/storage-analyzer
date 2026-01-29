package main

import (
	"context"
	"os/exec"
	"syscall"

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

// OpenFile opens the file or directory using the OS default application

func (a *App) OpenFile(path string) error {
	var cmd *exec.Cmd
	// Windows support
	cmd = exec.Command("cmd", "/c", "start", "", path)
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	// For cross-platform support we would check runtime.GOOS
	return cmd.Start()
}
