# Storage Analyzer

A Python-based storage analysis application for Windows that provides an interactive, user-friendly GUI to explore and analyze folder structures and storage usage with advanced sorting and visualization capabilities.

[English]

## Features
- Interactive folder tree visualization
- Real-time storage size calculation
- Percentage calculation of storage usage relative to parent folders
- Sortable columns (Name, Size, Percentage, Files, Path)
- Expandable/collapsible folder structure
- Error handling for inaccessible folders
- Human-readable size formatting (B, KB, MB, GB, TB, PB)

## Requirements
- Python 3.x
- tkinter (usually comes with Python)

## Usage
1. Run `python storage_analyzer.py`
2. Click "Select Folder" to choose a directory to analyze
3. Use the toolbar buttons to:
   - Refresh: Update the current folder analysis
   - Expand All: Open all folder trees
   - Collapse All: Close all folder trees
4. Click column headers to sort by:
   - Name: Alphabetical order of folder names
   - Size: Total storage size
   - %: Percentage of parent folder's size
   - Files: Number of files
   - Path: Full folder path

[日本語]

## 機能
- インタラクティブなフォルダツリーの可視化
- リアルタイムのストレージサイズ計算
- 親フォルダに対する使用率（パーセンテージ）の計算
- ソート可能な列（名前、サイズ、使用率、ファイル数、パス）
- フォルダ構造の展開/折りたたみ
- アクセス不可フォルダのエラー処理
- 人間が読みやすいサイズ表示（B、KB、MB、GB、TB、PB）

## 必要条件
- Python 3.x
- tkinter（通常Pythonに同梱）

## 使用方法
1. `python storage_analyzer.py` を実行
2. 「Select Folder」をクリックして分析するフォルダを選択
3. ツールバーボタンの機能：
   - Refresh：現在のフォルダ分析を更新
   - Expand All：すべてのフォルダツリーを展開
   - Collapse All：すべてのフォルダツリーを折りたたむ
4. 列ヘッダーをクリックしてソート：
   - Name：フォルダ名のアルファベット順
   - Size：合計ストレージサイズ
   - %：親フォルダに対するサイズの割合
   - Files：ファイル数
   - Path：フォルダの完全パス

## 今後の機能追加予定
- 複数フォルダの同時分析機能
- エクスポート機能（CSV、JSON形式）
