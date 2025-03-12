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
        self.tree["columns"] = ("size", "percentage", "files", "path")
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("size", width=100, minwidth=100)
        self.tree.column("percentage", width=70, minwidth=70)
        self.tree.column("files", width=70, minwidth=70)
        self.tree.column("path", width=260, minwidth=200)

        # Set headers
        self.tree.heading("#0", text="Name")
        self.tree.heading("size", text="Size")
        self.tree.heading("percentage", text="%")
        self.tree.heading("files", text="Files")
        self.tree.heading("path", text="Path")

        # Initialize sorting state
        self.sort_column = "name"
        self.sort_reverse = False

        # Bind events
        self.tree.bind('<<TreeviewOpen>>', self.on_open)
        self.tree.bind('<<TreeviewClose>>', self.on_close)
        self.tree.bind('<ButtonRelease-1>', self.on_header_click)

    def on_header_click(self, event):
        """Handle header click event"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            # Convert column identifier (#1, #2, etc.) to column name
            column_index = int(column.replace('#', ''))
            if column_index == 0:
                self.sort_tree("name")
            else:
                # Map column index to column name
                columns = ["size", "percentage", "files", "path"]
                if column_index <= len(columns):
                    self.sort_tree(columns[column_index - 1])

    def sort_tree(self, column):
        """Sort tree content when a column header is clicked"""
        items = []
        parent = ""  # Sort only top-level items

        # Change sort direction if clicking the same column
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        self.sort_column = column

        # Get all top-level items
        for item in self.tree.get_children(parent):
            values = self.tree.item(item)
            items.append((values["text"], values["values"], item))

        # Sort items based on column
        items.sort(key=lambda x: self._get_sort_key(x, column), reverse=self.sort_reverse)

        # Rearrange items in sorted order
        for index, (_, _, item) in enumerate(items):
            self.tree.move(item, parent, index)

    def _get_sort_key(self, item, column):
        """Get the sorting key based on column"""
        text, values, _ = item
        if column == "name":
            # Remove folder icon and error indicators for sorting
            return text.replace("🗀 ", "").replace(" (⚠️ Access denied)", "").lower()
        elif column == "size":
            # Extract numeric value from size string
            size_str = values[0]
            try:
                number = float(size_str.split()[0])
                unit = size_str.split()[1]
                # Convert to bytes for comparison
                multiplier = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4, "PB": 1024**5}
                return number * multiplier.get(unit, 0)
            except:
                return 0
        elif column == "percentage":
            try:
                return float(values[1]) if values[1] else 0
            except:
                return 0
        elif column == "files":
            try:
                return int(values[2])
            except:
                return 0
        elif column == "path":
            return values[3].lower()
        return ""

    def clear(self):
        """Clear the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate(self, data: Dict[str, Any], parent: str = "", parent_size: float = None):
        """Add data to the treeview"""
        if data['type'] != 'directory':
            return

        # Format size and create display text
        size_str = self._format_size(data['size'])
        files_count = data['file_count']

        # Calculate percentage if parent exists
        percentage = ""
        if parent_size is not None and parent_size > 0:
            percentage = f"{(data['size'] / parent_size) * 100:.1f}"

        # Handle error display
        if 'error' in data:
            item_text = f"🗀 {data['name']} (⚠️ {data['error']})"
        else:
            item_text = f"🗀 {data['name']}"

        # Add item
        item_id = self.tree.insert(
            parent, 'end',
            text=item_text,
            values=(size_str, percentage, files_count, data['path'])
        )

        # Add children (only directories)
        if 'children' in data:
            for child in data['children']:
                if child['type'] == 'directory':
                    self.populate(child, item_id, data['size'])

    def get_selected_path(self) -> Optional[str]:
        """Get the path of the selected item"""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])['values'][3]  # Path is now at index 3
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