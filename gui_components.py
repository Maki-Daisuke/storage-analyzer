import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

class StorageTreeView:
    def __init__(self, parent):
        # Treeviewの作成
        self.tree = ttk.Treeview(parent)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # スクロールバーの追加
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # カラムの設定
        self.tree["columns"] = ("size", "path")
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("size", width=100, minwidth=100)
        self.tree.column("path", width=400, minwidth=200)

        # ヘッダーの設定
        self.tree.heading("#0", text="名前")
        self.tree.heading("size", text="サイズ")
        self.tree.heading("path", text="パス")

        # イベントバインド
        self.tree.bind('<<TreeviewOpen>>', self.on_open)
        self.tree.bind('<<TreeviewClose>>', self.on_close)

    def clear(self):
        """ツリービューをクリア"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate(self, data: Dict[str, Any], parent: str = ""):
        """ツリービューにデータを追加"""
        # アイコンの選択
        icon = "🗀" if data['type'] == 'directory' else "📄"
        
        # サイズのフォーマット
        size_str = self._format_size(data['size'])
        
        # エラー表示の処理
        if 'error' in data:
            item_text = f"{icon} {data['name']} (⚠️ {data['error']})"
        else:
            item_text = f"{icon} {data['name']}"

        # アイテムの追加
        item_id = self.tree.insert(
            parent, 'end',
            text=item_text,
            values=(size_str, data['path'])
        )

        # 子要素の追加
        if 'children' in data:
            for child in data['children']:
                self.populate(child, item_id)

    def get_selected_path(self) -> Optional[str]:
        """選択されているアイテムのパスを取得"""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])['values'][1]
        return None

    def expand_all(self):
        """すべての項目を展開"""
        def expand_recursive(item):
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                expand_recursive(child)

        for item in self.tree.get_children():
            expand_recursive(item)

    def collapse_all(self):
        """すべての項目を折りたたむ"""
        def collapse_recursive(item):
            self.tree.item(item, open=False)
            for child in self.tree.get_children(item):
                collapse_recursive(child)

        for item in self.tree.get_children():
            collapse_recursive(item)

    def on_open(self, event):
        """フォルダを開いたときの処理"""
        pass

    def on_close(self, event):
        """フォルダを閉じたときの処理"""
        pass

    @staticmethod
    def _format_size(size: int) -> str:
        """バイト数を人間が読みやすい形式に変換"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
