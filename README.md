# Storage Analyzer (ストレージ解析ツール)

![Screenshot](https://github.com/user-attachments/assets/c064d213-495d-4365-aff5-d245eb3db68a)

ストレージ使用状況を分析・可視化するPythonベースのGUIアプリケーションです。
フォルダ構造を探索し、ストレージの使用状況を詳細に分析することができます。

## 主な機能

- 🌳 対話的なフォルダツリービュー（サイズ情報付き）
- 📋 ソート可能な列（名前、サイズ、ファイル数、パス）

## インストール方法

```bash
pip install storage-analyzer
```

または、Poetry経由でインストール：

```bash
poetry add storage-analyzer
```

## 使用方法

1. アプリケーションを起動：
```bash
storage-analyzer
```

2. 「Select Folder」ボタンをクリックして、分析したいフォルダを選択します。
3. フォルダツリーが表示され、各フォルダのサイズや内容を確認できます。
4. 列ヘッダーをクリックすることで、異なる基準でソートができます。

## 要件

- Python 3.8以上
- tkinter（標準のPythonディストリビューションに含まれています）

## 開発者向け情報

プロジェクトの開発に参加する場合：

```bash
# リポジトリのクローン
git clone https://github.com/username/storage-analyzer.git

# 依存関係のインストール
poetry install

# 開発用サーバーの起動
poetry run storage-analyzer
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
