//go:build windows

package main

import (
	"fmt"
	"os"
	"syscall"
	"unsafe"
)

var (
	kernel32                  = syscall.NewLazyDLL("kernel32.dll")
	procGetCompressedFileSize = kernel32.NewProc("GetCompressedFileSizeW")
)

// getPhysicalSize returns the actual disk space used by the file.
// On Windows, this uses GetCompressedFileSizeW which accounts for
// compressed files, sparse files, and NTFS allocation.
func getPhysicalSize(path string, info os.FileInfo) int64 {
	pathPtr, err := syscall.UTF16PtrFromString(path)
	if err != nil {
		panic(fmt.Errorf("failed to convert path %s to UTF16: %w", path, err))
	}

	var high uint32
	low, _, callErr := procGetCompressedFileSize.Call(
		uintptr(unsafe.Pointer(pathPtr)),
		uintptr(unsafe.Pointer(&high)),
	)

	// Check for error: low == INVALID_FILE_SIZE (0xFFFFFFFF) and error is set
	if low == 0xFFFFFFFF && callErr != syscall.Errno(0) {
		// Fallback to logical size
		return info.Size()
	}

	return int64(high)<<32 | int64(low)
}
