import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui_components import StorageTreeView
from folder_scanner import FolderScanner
import threading

class StorageAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ストレージ分析ツール")
        self.root.geometry("800x600")
        
        # メインフレームの設定
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ツールバーの作成
        self.create_toolbar()
        
        # Treeviewの作成
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = StorageTreeView(self.tree_frame)
        self.scanner = FolderScanner()
        
        # ステータスバーの作成
        self.status_var = tk.StringVar()
        self.status_var.set("フォルダを選択してください")
        self.statusbar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_toolbar(self):
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="フォルダ選択", command=self.select_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="更新", command=self.refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="すべて展開", command=self.expand_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="すべて折りたたむ", command=self.collapse_all).pack(side=tk.LEFT, padx=2)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="分析するフォルダを選択")
        if folder_path:
            self.status_var.set("分析中...")
            self.tree.clear()
            
            # 非同期で処理を実行
            thread = threading.Thread(target=self.scan_folder, args=(folder_path,))
            thread.daemon = True
            thread.start()

    def scan_folder(self, folder_path):
        try:
            folder_data = self.scanner.scan(folder_path)
            self.root.after(0, self.update_tree, folder_data)
            self.root.after(0, self.status_var.set, "分析完了")
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def update_tree(self, folder_data):
        self.tree.populate(folder_data)

    def show_error(self, message):
        messagebox.showerror("エラー", message)
        self.status_var.set("エラーが発生しました")

    def refresh(self):
        current_selection = self.tree.get_selected_path()
        if current_selection:
            self.select_folder(current_selection)

    def expand_all(self):
        self.tree.expand_all()

    def collapse_all(self):
        self.tree.collapse_all()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StorageAnalyzer()
    app.run()
