import os
from pathlib import Path
from typing import Dict, Any
import logging

class FolderScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def scan(self, root_path: str) -> Dict[str, Any]:
        """フォルダを再帰的にスキャンし、容量情報を収集"""
        try:
            root = Path(root_path)
            return self._scan_directory(root)
        except Exception as e:
            self.logger.error(f"Scanning error: {str(e)}")
            raise

    def _scan_directory(self, path: Path) -> Dict[str, Any]:
        """ディレクトリの容量情報を収集"""
        result = {
            'name': path.name or str(path),
            'path': str(path),
            'size': 0,
            'children': [],
            'type': 'directory'
        }

        try:
            # ディレクトリ内のファイルとフォルダを走査
            for item in path.iterdir():
                if item.is_file():
                    size = item.stat().st_size
                    result['size'] += size
                    result['children'].append({
                        'name': item.name,
                        'path': str(item),
                        'size': size,
                        'type': 'file'
                    })
                elif item.is_dir():
                    try:
                        subdir_info = self._scan_directory(item)
                        result['size'] += subdir_info['size']
                        result['children'].append(subdir_info)
                    except PermissionError:
                        self.logger.warning(f"Permission denied: {item}")
                        result['children'].append({
                            'name': item.name,
                            'path': str(item),
                            'size': 0,
                            'type': 'directory',
                            'error': 'アクセス権限がありません'
                        })

        except PermissionError:
            self.logger.warning(f"Permission denied while scanning: {path}")
            result['error'] = 'アクセス権限がありません'
        except Exception as e:
            self.logger.error(f"Error scanning directory {path}: {str(e)}")
            result['error'] = f'スキャンエラー: {str(e)}'

        return result

    @staticmethod
    def format_size(size: int) -> str:
        """バイト数を人間が読みやすい形式に変換"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
