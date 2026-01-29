# Storage Analyzer (ストレージ解析ツール)

![Screenshot](https://github.com/user-attachments/assets/6682308a-cacd-42d2-a56d-d6e7b471e789)

ストレージ使用状況を分析・可視化するデスクトップアプリケーションです。

## 主な機能

- 🌳 **高速なフォルダスキャン**:
  - 並行処理によるファイルシステム探索
  - 環境変数 `SCAN_CONCURRENCY` で並行実行数を調整可能（デフォルト: 4）
- 📊 **詳細な情報表示**:
  - ファイル/フォルダ名
  - サイズ (自動単位変換)
  - 全体に対する割合（パーセント表示 + バーグラフ）
  - ファイル数
- 📋 **ソート機能**: 各カラム（名前、サイズ、割合、ファイル数）での並び替え
- 🔄 **リフレッシュ機能**: 最新のフォルダ構造を再スキャンして反映
- 📂 **ファイルオープン**: ダブルクリックでファイル/フォルダをOS標準のアプリで開く
- ⚠️ **エラーハンドリング**: アクセス権限のないフォルダの可視化

## システム構成

本アプリケーションは [Wails](https://wails.io/) フレームワークを使用しています。

- **Frontend**: Svelte + Vite (HTML/CSS/JS)
- **Backend**: Golang (システムコール、ファイル操作)
- **Communication**: Wails runtime (Frontend-Backend間のバインディング)

## ディレクトリ構成

```
storage-analyzer/
├── app.go              # Wails アプリケーションロジック (FrontendへのAPI定義)
├── scanner.go          # フォルダスキャン・サイズ計算ロジック (Go)
├── main.go             # エントリーポイント
├── frontend/           # フロントエンド (Svelte)
│   ├── src/
│   │   ├── lib/
│   │   │   └── components/
│   │   │       └── FileTree.svelte  # 再帰的ファイルツリーコンポーネント
│   │   ├── App.svelte               # メインUI・ソートロジック
│   │   └── style.css                # グローバルスタイル (Dark Theme)
│   └── wailsjs/        # 自動生成されるGoバインディング (JS)
└── build/              # ビルド成果物および設定
```

## 開発・ビルド方法

### 必要要件

- **Go** 1.24+
- **Node.js** 16+
- **Wails CLI**: `go install github.com/wailsapp/wails/v2/cmd/wails@latest`

### 開発モード (Live Reload)

```bash
wails dev
```
アプリケーションがウィンドウモードで起動し、ソースコード変更時に自動リロードされます。

### 本番ビルド

```bash
wails build
```
`build/bin/` ディレクトリに実行ファイル (`storage-analyzer.exe`) が生成されます。

## ライセンス

MIT License

## Author

Daisuke (yet another) Maki
