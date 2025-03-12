import os
from pathlib import Path
from typing import Dict, Any, Callable
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.logger = logging.getLogger(__name__)

    def on_any_event(self, event):
        if isinstance(event, (FileModifiedEvent, FileCreatedEvent, FileDeletedEvent)):
            try:
                # Get the parent directory of the changed file
                parent_dir = str(Path(event.src_path).parent)
                self.logger.debug(f"File system change detected in: {parent_dir}")
                self.callback(parent_dir)
            except Exception as e:
                self.logger.error(f"Error handling file system event: {str(e)}")

class FolderScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.observer = None
        self.handler = None

    def start_monitoring(self, callback: Callable[[str], None]):
        """Start monitoring file system changes"""
        self.handler = FolderChangeHandler(callback)
        self.observer = Observer()
        self.observer.start()
        self.logger.debug("Started file system observer")

    def add_watch_path(self, path: str):
        """Add a path to watch for changes"""
        if self.observer and self.handler:
            try:
                self.observer.schedule(self.handler, path, recursive=True)
                self.logger.debug(f"Started monitoring path: {path}")
            except Exception as e:
                self.logger.error(f"Error setting up file system monitor: {str(e)}")

    def stop_monitoring(self):
        """Stop monitoring file system changes"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.debug("Stopped file system monitoring")

    def scan(self, root_path: str) -> Dict[str, Any]:
        """Recursively scan folder and collect storage information"""
        try:
            root = Path(root_path)
            return self._scan_directory(root)
        except Exception as e:
            self.logger.error(f"Scanning error: {str(e)}")
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
                elif item.is_dir():
                    try:
                        subdir_info = self._scan_directory(item)
                        result['size'] += subdir_info['size']
                        result['file_count'] += subdir_info['file_count']
                        result['children'].append(subdir_info)
                    except PermissionError:
                        self.logger.warning(f"Permission denied: {item}")
                        result['children'].append({
                            'name': item.name,
                            'path': str(item),
                            'size': 0,
                            'file_count': 0,
                            'type': 'directory',
                            'error': 'Access denied'
                        })

        except PermissionError:
            self.logger.warning(f"Permission denied while scanning: {path}")
            result['error'] = 'Access denied'
        except Exception as e:
            self.logger.error(f"Error scanning directory {path}: {str(e)}")
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