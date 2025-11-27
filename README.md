# file-diff-tool

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
