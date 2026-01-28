import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .gui_components import StorageTreeView
from .folder_scanner import FolderScanner
import threading
import time

class StorageAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Storage Analyzer")
        self.root.geometry("800x600")

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
            self.status_var.set("Analyzing...")
            self.tree.clear()

            # Run analysis in a separate thread
            thread = threading.Thread(target=self.scan_folder, args=(folder_path,))
            thread.daemon = True
            thread.start()

    def scan_folder(self, folder_path):
        last_update = 0
        
        def on_progress(count):
            nonlocal last_update
            current_time = time.time()
            if current_time - last_update > 0.1:
                self.root.after(0, self.status_var.set, f"Scanning... {count} files found")
                last_update = current_time

        try:
            folder_data = self.scanner.scan(folder_path, progress_callback=on_progress)
            self.root.after(0, self.update_tree, folder_data)
            self.root.after(0, self.status_var.set, "Analysis complete")
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def update_tree(self, folder_data):
        self.tree.populate(folder_data)

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.status_var.set("An error occurred")

    def refresh(self):
        current_selection = self.tree.get_selected_path()
        if current_selection:
            self.select_folder()

    def expand_all(self):
        self.tree.expand_all()

    def collapse_all(self):
        self.tree.collapse_all()

    def run(self):
        self.root.mainloop()

def main():
    app = StorageAnalyzer()
    app.run()

if __name__ == "__main__":
    main()