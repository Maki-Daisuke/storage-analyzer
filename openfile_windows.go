//go:build windows

package main

import (
	"os/exec"
	"syscall"
)

func (a *App) OpenFile(path string) error {
	cmd := exec.Command("cmd", "/c", "start", "", path)
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	return cmd.Start()
}
