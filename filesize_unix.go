//go:build !windows

package main

import (
	"os"
	"syscall"
)

// getPhysicalSize returns the actual disk space used by the file.
// On Unix systems, this uses stat.Blocks * 512 which accounts for
// sparse files and filesystem block allocation.
func getPhysicalSize(path string, info os.FileInfo) int64 {
	stat, ok := info.Sys().(*syscall.Stat_t)
	if !ok {
		// Fallback to logical size if syscall info is not available
		return info.Size()
	}
	// Blocks is always in 512-byte units (POSIX standard)
	return stat.Blocks * 512
}
