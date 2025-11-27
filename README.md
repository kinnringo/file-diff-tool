# File Diff Tool

脆弱性診断の再診断時に、修正前後のディレクトリを比較し、変更箇所を効率的に把握するためのPythonツールです。

2つのディレクトリを比較し、新規追加・削除・変更されたファイルを検出して、視覚的に見やすいHTML形式のレポートを生成します。

## インストール

Python 3.6以降が必要。標準ライブラリのみを使用するため、追加のパッケージインストールは不要です。

## 使用方法

```bash
python diff_report.py <旧ディレクトリ> <新ディレクトリ> [オプション]
```

### 基本例
```bash
python diff_report.py ./before ./after
```

### オプション
- `-o`, `--output`: 出力HTMLファイル名（デフォルト: diff_report.html）
- `-e`, `--extensions`: 対象ファイル拡張子（デフォルト: .php）

### 例: 複数の拡張子を指定
```bash
python diff_report.py ./before ./after -e .php .js .css
```

### 例: 出力ファイル名を指定
```bash
python diff_report.py ./before ./after -o report_20250127.html
```
