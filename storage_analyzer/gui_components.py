import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List
import logging
import copy

class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None

    def show_tip(self, text, x, y):
        if self.tip_window or not text:
            return
        
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x+10}+{y+10}")

        label = ttk.Label(self.tip_window, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class StorageTreeView:
    def __init__(self, parent):
        self.logger = logging.getLogger(__name__)
        # logging.basicConfig(level=logging.DEBUG)  # Removed to prevent unwanted output
        
        self.item_errors = {}
        self.tooltip = None
        self.last_tooltip_item = None

        # Create Treeview
        self.tree = ttk.Treeview(parent)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tooltip = ToolTip(self.tree)

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
        self.stored_data = None

        # Bind events
        self.tree.bind('<ButtonRelease-1>', self.on_header_click)
        self.tree.bind('<<TreeviewOpen>>', self.on_open)
        self.tree.bind('<<TreeviewClose>>', self.on_close)
        self.tree.bind('<Motion>', self.on_motion)

    def on_motion(self, event):
        item = self.tree.identify_row(event.y)
        
        if item != self.last_tooltip_item:
            self.tooltip.hide_tip()
            self.last_tooltip_item = item
            
            if item and item in self.item_errors:
                self.tooltip.show_tip(self.item_errors[item], event.x_root, event.y_root)

    def get_expanded_items(self) -> List[str]:
        """Get list of expanded item paths"""
        expanded = []
        def collect_expanded(item):
            if self.tree.item(item)['open']:
                values = self.tree.item(item)['values']
                if values:  # Check if values exist
                    expanded.append(values[3])  # Path is at index 3
            for child in self.tree.get_children(item):
                collect_expanded(child)
        
        for item in self.tree.get_children():
            collect_expanded(item)
        return expanded

    def expand_items_by_path(self, expanded_paths: List[str]):
        """Expand items based on their paths"""
        def expand_by_path(item):
            values = self.tree.item(item)['values']
            if values and values[3] in expanded_paths:
                self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                expand_by_path(child)

        for item in self.tree.get_children():
            expand_by_path(item)

    def on_header_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        self.logger.debug(f"Clicked region: {region}")

        if region == "heading":
            column = self.tree.identify_column(event.x)
            column_index = int(column.replace('#', ''))
            self.logger.debug(f"Clicked column index: {column_index}")

            column_name = "name" if column_index == 0 else ["size", "percentage", "files", "path"][column_index - 1]
            self.logger.debug(f"Selected column for sorting: {column_name}")

            # Toggle sort direction if same column
            if self.sort_column == column_name:
                self.sort_reverse = not self.sort_reverse
            else:
                self.sort_column = column_name
                self.sort_reverse = False
            
            self.logger.debug(f"Sort direction reversed: {self.sort_reverse}")

            # Rebuild tree with new sorting
            if self.stored_data:
                self.logger.debug("Rebuilding tree with sorted data")
                # Store expanded state
                expanded_paths = self.get_expanded_items()
                self.logger.debug(f"Stored expanded paths: {expanded_paths}")

                self.clear()
                self.populate(copy.deepcopy(self.stored_data))

                # Restore expanded state
                self.expand_items_by_path(expanded_paths)
                self.logger.debug("Restored expanded state")

    def sort_items(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get('children'):
            return data

        self.logger.debug(f"Sorting children by {self.sort_column} {'descending' if self.sort_reverse else 'ascending'}")

        # Sort children based on current sort settings
        data['children'].sort(key=lambda x: self.get_sort_key(x), reverse=self.sort_reverse)

        # Recursively sort child folders
        for child in data['children']:
            if child['type'] == 'directory':
                self.sort_items(child)
        
        return data

    def get_sort_key(self, item: Dict[str, Any]):
        if self.sort_column == "name":
            return item['name'].lower()
        elif self.sort_column == "size":
            return item['size']
        elif self.sort_column == "percentage":
            return item.get('percentage', 0)
        elif self.sort_column == "files":
            return item['file_count']
        elif self.sort_column == "path":
            return item['path'].lower()
        return ""

    def clear(self):
        """Clear the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.item_errors.clear()
        if self.tooltip:
            self.tooltip.hide_tip()

    def populate(self, data: Dict[str, Any], parent: str = "", parent_size: float = None):
        """Add data to the treeview"""
        # Store the original data for sorting
        if parent == "":
            self.logger.debug("Storing initial data for sorting")
            self.stored_data = copy.deepcopy(data)
            data = self.sort_items(data)

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
            item_text = f"⚠️{data['name']}"
        else:
            item_text = f"🗀 {data['name']}"

        # Add item
        item_id = self.tree.insert(
            parent, 'end',
            text=item_text,
            values=(size_str, percentage, files_count, data['path'])
        )
        
        if 'error' in data:
            self.item_errors[item_id] = data['error']

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
        self.logger.debug("Folder opened")
        pass

    def on_close(self, event):
        """Handle folder close event"""
        self.logger.debug("Folder closed")
        pass

    @staticmethod
    def _format_size(size: float) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"