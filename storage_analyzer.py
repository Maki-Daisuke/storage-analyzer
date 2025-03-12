import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui_components import StorageTreeView
from folder_scanner import FolderScanner
import threading
import logging

class StorageAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Storage Analyzer")
        self.root.geometry("800x600")

        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # Main frame setup
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create toolbar
        self.create_toolbar()

        # Create Treeview
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = StorageTreeView(self.tree_frame)
        self.scanner = FolderScanner()

        # Start file system monitoring
        self.scanner.start_monitoring(self.on_folder_change)

        # Store current folder path
        self.current_folder = None

        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Please select a folder to analyze")
        self.statusbar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_toolbar(self):
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Expand All", command=self.expand_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Collapse All", command=self.collapse_all).pack(side=tk.LEFT, padx=2)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder to analyze")
        if folder_path:
            self.current_folder = folder_path
            self.status_var.set("Analyzing...")
            self.tree.clear()

            # Start monitoring the selected folder
            self.scanner.add_watch_path(folder_path)

            # Run analysis in a separate thread
            thread = threading.Thread(target=self.scan_folder, args=(folder_path,))
            thread.daemon = True
            thread.start()

    def on_folder_change(self, changed_path: str):
        """Handle folder content changes"""
        self.logger.debug(f"Folder change detected: {changed_path}")
        if self.current_folder and (
            changed_path == self.current_folder or 
            changed_path.startswith(self.current_folder)
        ):
            self.root.after(1000, self.delayed_refresh)  # Delay refresh to avoid multiple updates

    def delayed_refresh(self):
        """Refresh after a delay to avoid multiple rapid updates"""
        if self.current_folder:
            self.status_var.set("Updating...")
            thread = threading.Thread(target=self.scan_folder, args=(self.current_folder,))
            thread.daemon = True
            thread.start()

    def scan_folder(self, folder_path):
        try:
            folder_data = self.scanner.scan(folder_path)
            self.root.after(0, self.update_tree, folder_data)
            self.root.after(0, self.status_var.set, "Analysis complete")
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def update_tree(self, folder_data):
        # Store expanded state before update
        expanded_paths = self.tree.get_expanded_items()

        # Update tree with new data
        self.tree.populate(folder_data)

        # Restore expanded state
        self.tree.expand_items_by_path(expanded_paths)

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.status_var.set("An error occurred")

    def refresh(self):
        if self.current_folder:
            self.select_folder()

    def expand_all(self):
        self.tree.expand_all()

    def collapse_all(self):
        self.tree.collapse_all()

    def run(self):
        try:
            self.root.mainloop()
        finally:
            # Cleanup when application closes
            self.scanner.stop_monitoring()

if __name__ == "__main__":
    app = StorageAnalyzer()
    app.run()