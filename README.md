# Duminous (Storage Analyzer)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Report Card](https://goreportcard.com/badge/github.com/Maki-Daisuke/duminous)](https://goreportcard.com/report/github.com/Maki-Daisuke/duminous)

A simple desktop application to analyze and visualize storage usage.

![Screenshot](https://github.com/user-attachments/assets/1f82f945-011b-4c00-923f-9d3f461ff88f)

https://github.com/user-attachments/assets/6752a24a-48ab-4e74-8c78-e5fd1e8a3227

## Features

- 🌳 **Fast Folder Scanning**:
  - Concurrent file system exploration
  - Concurrency level adjustable via `SCAN_CONCURRENCY` environment variable (Default: Half of logical CPUs)
  - Correctly handles Symlinks and Windows Reparse Points (Junctions) to prevent infinite loops and incorrect size calculations
- 📊 **Detailed Information Display**:
  - File/Folder name
  - Size (automatic unit conversion)
  - Percentage of total usage (percent display + bar graph)
  - File count
- 💾 **Physical Disk Size Calculation**:
  - Toggle "Calculate Size on Disk" to measure actual disk usage
  - Accounts for sparse files, compression, and filesystem block allocation
- 📋 **Sorting**: Sort by any column (name, size, percentage, file count)
- 🔄 **Refresh**: Rescan to reflect the latest folder structure
- 📂 **Open File**: Double-click to open files/folders in the OS default application
- ⚠️ **Error Handling**: Visualization of inaccessible folders

## Installation

Go to the [Releases](https://github.com/Maki-Daisuke/duminous/releases) page and download the executable for your operating system.

## Architecture

This application uses the [Wails](https://wails.io/) framework.

- **Frontend**: Svelte + Vite (HTML/CSS/JS)
- **Backend**: Golang (System calls, File operations)
- **Communication**: Wails runtime (Frontend-Backend binding)

## Directory Structure

```
Duminous/
├── app.go              # Wails application logic (API definitions for Frontend)
├── scanner.go          # Folder scanning and size calculation logic (Go)
├── main.go             # Entry point
├── frontend/           # Frontend (Svelte)
│   ├── src/
│   │   ├── lib/
│   │   │   └── components/
│   │   │       └── FileTree.svelte  # Recursive file tree component
│   │   ├── App.svelte               # Main UI and sort logic
│   │   └── style.css                # Global styles (Dark Theme)
│   └── wailsjs/        # Automatically generated Go bindings (JS)
└── build/              # Build artifacts and configuration
```

## Development & Build

### Prerequisites

- **Go** 1.24+
- **Node.js** 16+
- **Wails CLI**: `go install github.com/wailsapp/wails/v2/cmd/wails@latest`

### Development Mode (Live Reload)

```bash
wails dev
```
The application will start in windowed mode and automatically reload on source code changes.

### Production Build

```bash
wails build
```
The executable file will be generated in the `build/bin/` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub Issues](https://github.com/Maki-Daisuke/duminous/issues) page.

## License

MIT License

## Author

**Daisuke (yet another) Maki** ([GitHub](https://github.com/Maki-Daisuke))
