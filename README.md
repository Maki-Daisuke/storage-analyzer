# Storage Analyzer (ストレージ解析ツール)

![Screenshot](https://github.com/user-attachments/assets/c064d213-495d-4365-aff5-d245eb3db68a)

ストレージ使用状況を分析・可視化するPythonベースのGUIアプリケーションです。
フォルダ構造を探索し、ストレージの使用状況を詳細に分析することができます。

## 主な機能

- 🌳 対話的なフォルダツリービュー（サイズ情報付き）
- 📋 ソート可能な列（名前、サイズ、パス、ファイル数、割合）
- 🔄 フォルダ構造の自動更新（Refresh機能）
- 📂 一括展開・折りたたみ機能（Expand/Collapse All）
- ⚠️ アクセス権限エラーの視覚的表示

## インストール方法

```bash
pip install storage-analyzer
```

または、`uv` を使用する場合：

```bash
uv add storage-analyzer
```

## 使用方法

1. アプリケーションを起動（インストール済みの場合）：
```bash
storage-analyzer
```

または、`uv` を使って直接実行：
```bash
uv run storage-analyzer
```

2. 「Select Folder」ボタンをクリックして、分析したいフォルダを選択します。
3. フォルダツリーが表示され、各フォルダのサイズや内容を確認できます。
4. ツールバーのボタンを使用して表示を操作できます：
   - **Refresh**: 現在のフォルダを再スキャンして情報を更新します
   - **Expand All**: 全てのフォルダを展開して表示します
   - **Collapse All**: 全てのフォルダを折りたたみます
5. 列ヘッダーをクリックすることで、異なる基準でソートができます。
6. ステータスバーでスキャンの進捗状況を確認できます。

## 要件

- Python 3.8以上
- tkinter（標準のPythonディストリビューションに含まれています）
- uv（開発・実行推奨）

## 開発者向け情報

プロジェクトの開発に参加する場合：

```bash
# リポジトリのクローン
git clone https://github.com/username/storage-analyzer.git
cd storage-analyzer

# 依存関係のインストール
uv sync

# アプリケーションの実行
uv run storage-analyzer
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
