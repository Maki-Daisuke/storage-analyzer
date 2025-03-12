import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

class StorageTreeView:
    def __init__(self, parent):
        # Create Treeview
        self.tree = ttk.Treeview(parent)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configure columns
        self.tree["columns"] = ("size", "files", "path")
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("size", width=100, minwidth=100)
        self.tree.column("files", width=70, minwidth=70)
        self.tree.column("path", width=330, minwidth=200)

        # Set headers
        self.tree.heading("#0", text="Name")
        self.tree.heading("size", text="Size")
        self.tree.heading("files", text="Files")
        self.tree.heading("path", text="Path")

        # Bind events
        self.tree.bind('<<TreeviewOpen>>', self.on_open)
        self.tree.bind('<<TreeviewClose>>', self.on_close)

    def clear(self):
        """Clear the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate(self, data: Dict[str, Any], parent: str = ""):
        """Add data to the treeview"""
        if data['type'] != 'directory':
            return

        # Format size and create display text
        size_str = self._format_size(data['size'])
        files_count = data['file_count']

        # Handle error display
        if 'error' in data:
            item_text = f"🗀 {data['name']} (⚠️ {data['error']})"
        else:
            item_text = f"🗀 {data['name']}"

        # Add item
        item_id = self.tree.insert(
            parent, 'end',
            text=item_text,
            values=(size_str, files_count, data['path'])
        )

        # Add children (only directories)
        if 'children' in data:
            for child in data['children']:
                if child['type'] == 'directory':
                    self.populate(child, item_id)

    def get_selected_path(self) -> Optional[str]:
        """Get the path of the selected item"""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])['values'][2]  # Path is now at index 2
        return None

    def expand_all(self):
        """Expand all items"""
        def expand_recursive(item):
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                expand_recursive(child)

        for item in self.tree.get_children():
            expand_recursive(item)

    def collapse_all(self):
        """Collapse all items"""
        def collapse_recursive(item):
            self.tree.item(item, open=False)
            for child in self.tree.get_children(item):
                collapse_recursive(child)

        for item in self.tree.get_children():
            collapse_recursive(item)

    def on_open(self, event):
        """Handle folder open event"""
        pass

    def on_close(self, event):
        """Handle folder close event"""
        pass

    @staticmethod
    def _format_size(size: float) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"