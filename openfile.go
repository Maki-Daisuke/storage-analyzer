//go:build !windows && !darwin

package main

import (
	"os/exec"
)

func (a *App) OpenFile(path string) error {
	cmd := exec.Command("xdg-open", path)
	return cmd.Start()
}
