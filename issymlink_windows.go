//go:build windows

package main

import (
	"io/fs"
	"sync"
	"syscall"
	"unsafe"
)

const (
	IO_REPARSE_TAG_SYMLINK     = syscall.IO_REPARSE_TAG_SYMLINK
	IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003
)

// fileStat is copied from types_windows.go.
// We use this struct to access the FileAttributes and ReparseTag.
type fileStat struct {
	name string

	// from ByHandleFileInformation, Win32FileAttributeData, Win32finddata, and GetFileInformationByHandleEx
	FileAttributes uint32
	CreationTime   syscall.Filetime
	LastAccessTime syscall.Filetime
	LastWriteTime  syscall.Filetime
	FileSizeHigh   uint32
	FileSizeLow    uint32

	// from Win32finddata and GetFileInformationByHandleEx
	ReparseTag uint32

	// what syscall.GetFileType returns
	filetype uint32

	// used to implement SameFile
	sync.Mutex
	path             string
	vol              uint32
	idxhi            uint32
	idxlo            uint32
	appendNameToPath bool
}

type eface struct {
	typ unsafe.Pointer
	ptr unsafe.Pointer
}

// unsafeCast converts a FileInfo to a pointer to its underlying fileStat.
// We bypass the type check to avoid the overhead of type assertion.
func unsafeCast(fi fs.FileInfo) *fileStat {
	return (*fileStat)((*eface)(unsafe.Pointer(&fi)).ptr)
}

// Contrary to its name, isSymLink returns true if the entry is a symbolic link, junction, or mount point.
// All of them are treated as "symlinks" to prevent infinite loops and double counting.
func isSymLink(entry fs.DirEntry) bool {
	info, err := entry.Info()
	if err != nil {
		panic(err)
	}
	fs := unsafeCast(info)
	return fs.FileAttributes&syscall.FILE_ATTRIBUTE_REPARSE_POINT != 0 && (fs.ReparseTag == IO_REPARSE_TAG_SYMLINK || fs.ReparseTag == IO_REPARSE_TAG_MOUNT_POINT)
}
