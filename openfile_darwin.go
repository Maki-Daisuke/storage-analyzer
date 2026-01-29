//go:build darwin

package main

import (
	"os/exec"
)

func (a *App) OpenFile(path string) error {
	cmd := exec.Command("open", path)
	return cmd.Start()
}
