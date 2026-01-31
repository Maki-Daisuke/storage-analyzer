package main

import (
	"os"
	"path/filepath"
	"strconv"
	"testing"
)

func TestScanner_Scan_Basic(t *testing.T) {
	tempDir := t.TempDir()

	// Create structure:
	// root/
	//   file1.txt (5 bytes)
	//   subdir/
	//     file2.txt (10 bytes)

	err := os.WriteFile(filepath.Join(tempDir, "file1.txt"), []byte("12345"), 0644)
	if err != nil {
		t.Fatal(err)
	}

	subDir := filepath.Join(tempDir, "subdir")
	err = os.Mkdir(subDir, 0755)
	if err != nil {
		t.Fatal(err)
	}

	err = os.WriteFile(filepath.Join(subDir, "file2.txt"), []byte("1234567890"), 0644)
	if err != nil {
		t.Fatal(err)
	}

	scanner := NewScanner(nil)
	node, err := scanner.Scan(tempDir)
	if err != nil {
		t.Fatalf("Scan failed: %v", err)
	}

	if node.Size != 15 {
		t.Errorf("Expected size 15, got %d", node.Size)
	}
	if node.FileCount != 2 {
		t.Errorf("Expected file count 2, got %d", node.FileCount)
	}
}

func TestScanner_Scan_Symlink(t *testing.T) {
	tempDir := t.TempDir()

	// Create structure:
	// root/
	//   real_dir/
	//     file.txt (5 bytes)
	//   link_to_dir -> real_dir

	realDir := filepath.Join(tempDir, "real_dir")
	err := os.Mkdir(realDir, 0755)
	if err != nil {
		t.Fatal(err)
	}

	err = os.WriteFile(filepath.Join(realDir, "file.txt"), []byte("12345"), 0644)
	if err != nil {
		t.Fatal(err)
	}

	linkPath := filepath.Join(tempDir, "link_to_dir")
	// Note: Symlinks on Windows might require admin privileges or developer mode.
	// If this fails, we might skip or handle gracefully, but we want to test logic.
	err = os.Symlink(realDir, linkPath)
	if err != nil {
		t.Skipf("Skipping symlink test due to error (likely permission): %v", err)
	}

	scanner := NewScanner(nil)
	node, err := scanner.Scan(tempDir)
	if err != nil {
		t.Fatalf("Scan failed: %v", err)
	}

	// Total size should be real file size + symlink size (0 in our logic).
	// Real dir: 5 bytes, 1 file
	// Symlink: 0 bytes, 1 file (treated as file)
	// Total: 5 bytes, 2 files

	if node.Size != 5 {
		t.Errorf("Expected size 5, got %d", node.Size)
	}
	// Verify that the recursion didn't follow the link as a directory
	// If it followed, it might see it as directory containing files.
	// Our logic says "Treat as file (leaf)", so fileCount should include the symlink itself as 1.
	if node.FileCount != 2 {
		t.Errorf("Expected file count 2, got %d", node.FileCount)
	}
}

func TestScanner_Scan_ConcurrencyLarge(t *testing.T) {
	tempDir := t.TempDir()

	// Create 50 directories, each with 10 files
	numDirs := 50
	filesPerDir := 10
	fileContent := []byte("12345") // 5 bytes

	for i := 0; i < numDirs; i++ {
		dirName := filepath.Join(tempDir, "dir"+strconv.Itoa(i))
		if err := os.Mkdir(dirName, 0755); err != nil {
			t.Fatal(err)
		}
		for j := 0; j < filesPerDir; j++ {
			fileName := filepath.Join(dirName, "file"+strconv.Itoa(j)+".txt")
			if err := os.WriteFile(fileName, fileContent, 0644); err != nil {
				t.Fatal(err)
			}
		}
	}

	scanner := NewScanner(nil)
	node, err := scanner.Scan(tempDir)
	if err != nil {
		t.Fatalf("Scan failed: %v", err)
	}

	expectedFiles := numDirs * filesPerDir
	expectedSize := int64(expectedFiles * len(fileContent))

	if node.FileCount != expectedFiles {
		t.Errorf("Expected file count %d, got %d", expectedFiles, node.FileCount)
	}

	if node.Size != expectedSize {
		t.Errorf("Expected size %d, got %d", expectedSize, node.Size)
	}
}

func TestScanner_Scan_DeepAndWide(t *testing.T) {
	tempDir := t.TempDir()

	width := 20
	depth := 10
	filesPerDir := 5
	fileContent := []byte("123") // 3 bytes

	var expectedFiles int
	var expectedSize int64

	// Helper to create nested structure
	var createNested func(parent string, currentDepth int)
	createNested = func(parent string, currentDepth int) {
		if currentDepth > depth {
			return
		}

		// Create files in current directory
		for i := 0; i < filesPerDir; i++ {
			fName := filepath.Join(parent, "file"+strconv.Itoa(i)+".txt")
			if err := os.WriteFile(fName, fileContent, 0644); err != nil {
				t.Fatal(err)
			}
			expectedFiles++
			expectedSize += int64(len(fileContent))
		}

		// Create subdirectory if valid depth
		if currentDepth < depth {
			subDir := filepath.Join(parent, "sub"+strconv.Itoa(currentDepth))
			if err := os.Mkdir(subDir, 0755); err != nil {
				t.Fatal(err)
			}
			createNested(subDir, currentDepth+1)
		}
	}

	// Create wide structure
	for i := 0; i < width; i++ {
		rootDir := filepath.Join(tempDir, "root"+strconv.Itoa(i))
		if err := os.Mkdir(rootDir, 0755); err != nil {
			t.Fatal(err)
		}
		createNested(rootDir, 1)
	}

	scanner := NewScanner(nil)
	node, err := scanner.Scan(tempDir)
	if err != nil {
		t.Fatalf("Scan failed: %v", err)
	}

	if node.FileCount != expectedFiles {
		t.Errorf("Expected file count %d, got %d", expectedFiles, node.FileCount)
	}

	if node.Size != expectedSize {
		t.Errorf("Expected size %d, got %d", expectedSize, node.Size)
	}
}

