"""Storage Analyzer Package

A Python-based storage analysis application for Windows that provides an interactive, 
user-friendly GUI to explore and analyze folder structures and storage usage.
"""

from .storage_analyzer import main
from .gui_components import StorageTreeView
from .folder_scanner import FolderScanner

__version__ = "0.1.0"
