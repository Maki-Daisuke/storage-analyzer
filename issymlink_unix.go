//go:build !windows

package main

import (
	"io/fs"
	"os"
)

// isSymLink checks if the entry is a symbolic link.
// On Unix-like systems, os.ModeSymlink is sufficient.
func isSymLink(entry fs.DirEntry) bool {
	return entry.Type()&os.ModeSymlink != 0
}
