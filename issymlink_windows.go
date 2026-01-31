//go:build windows

package main

import (
	"io/fs"
	"syscall"
	"unsafe"
)

// isSymLink checks if the entry is a symbolic link.
// Actually, this function checks if the entry is a reparse point (Symlink, Junction, etc.)
// to ignore all kind of reparse points  using FILE_ATTRIBUTE_REPARSE_POINT
// which correctly identifies Windows junction points.
func isSymLink(entry fs.DirEntry) bool {
	info, err := entry.Info()
	if err != nil {
		panic(err)
	}
	return unsafeCast(info.Sys()).FileAttributes&syscall.FILE_ATTRIBUTE_REPARSE_POINT != 0
}

type eface struct {
	typ unsafe.Pointer
	ptr unsafe.Pointer
}

// unsafeCast converts an interface to a pointer to its underlying data.
// This is equivalent to the following code:
//
//	sys, ok := info.Sys().(*syscall.Win32FileAttributeData)
//	return sys
//
// We bypass the type check to avoid the overhead of type assertion.
func unsafeCast(s any) *syscall.Win32FileAttributeData {
	return (*syscall.Win32FileAttributeData)((*eface)(unsafe.Pointer(&s)).ptr)
}
