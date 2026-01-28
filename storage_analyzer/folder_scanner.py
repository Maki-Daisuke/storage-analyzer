import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import logging

class FolderScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scanned_count = 0
        self.progress_callback = None

    def scan(self, root_path: str, progress_callback: Optional[Callable[[int], None]] = None) -> Dict[str, Any]:
        """Recursively scan folder and collect storage information"""
        self.scanned_count = 0
        self.progress_callback = progress_callback
        try:
            root = Path(root_path)
            return self._scan_directory(root)
        except Exception as e:
            self.logger.debug(f"Scanning error: {str(e)}")
            raise

    def _scan_directory(self, path: Path) -> Dict[str, Any]:
        """Collect directory storage information"""
        result = {
            'name': path.name or str(path),
            'path': str(path),
            'size': 0,
            'file_count': 0,
            'children': [],
            'type': 'directory'
        }

        try:
            # Scan files and folders in directory
            for item in path.iterdir():
                if item.is_file():
                    size = item.stat().st_size
                    result['size'] += size
                    result['file_count'] += 1
                    
                    self.scanned_count += 1
                    if self.progress_callback and self.scanned_count % 100 == 0:
                        self.progress_callback(self.scanned_count)
                elif item.is_dir():
                    try:
                        subdir_info = self._scan_directory(item)
                        result['size'] += subdir_info['size']
                        result['file_count'] += subdir_info['file_count']
                        result['children'].append(subdir_info)
                    except PermissionError:
                        self.logger.debug(f"Permission denied: {item}")
                        result['children'].append({
                            'name': item.name,
                            'path': str(item),
                            'size': 0,
                            'file_count': 0,
                            'type': 'directory',
                            'error': 'Access denied'
                        })

        except PermissionError:
            self.logger.debug(f"Permission denied while scanning: {path}")
            result['error'] = 'Access denied'
        except Exception as e:
            self.logger.debug(f"Error scanning directory {path}: {str(e)}")
            result['error'] = f'Scan error: {str(e)}'

        return result

    @staticmethod
    def format_size(size: float) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"