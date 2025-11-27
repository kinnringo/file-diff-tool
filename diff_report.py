#!/usr/bin/env python3
import os
import sys
import argparse
import difflib
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime


class DiffReport:
    def __init__(self, old_dir: str, new_dir: str, extensions: List[str]):
        self.old_dir = Path(old_dir)
        self.new_dir = Path(new_dir)
        self.extensions = extensions
        self.added_files = []
        self.deleted_files = []
        self.modified_files = []
        self.old_all_files = []
        self.new_all_files = []
        self.old_file_paths = {}
        self.new_file_paths = {}

    def scan_directories(self):
        old_files = self._get_files(self.old_dir)
        new_files = self._get_files(self.new_dir)
        
        self.old_all_files = sorted(old_files.keys())
        self.new_all_files = sorted(new_files.keys())
        self.old_file_paths = old_files
        self.new_file_paths = new_files
        
        old_set = set(old_files.keys())
        new_set = set(new_files.keys())
        
        self.added_files = sorted(new_set - old_set)
        self.deleted_files = sorted(old_set - new_set)
        common_files = sorted(old_set & new_set)
        
        for rel_path in common_files:
            old_content = self._read_file(old_files[rel_path])
            new_content = self._read_file(new_files[rel_path])
            
            if old_content != new_content:
                diff = self._generate_diff(old_content, new_content, rel_path)
                self.modified_files.append((rel_path, diff))

    def _get_files(self, directory: Path) -> Dict[str, Path]:
        files = {}
        for ext in self.extensions:
            for file_path in directory.rglob(f"*{ext}"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(directory)
                    files[str(rel_path)] = file_path
        return files

    def _read_file(self, file_path: Path) -> List[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='shift_jis') as f:
                return f.readlines()

    def _generate_diff(self, old_lines: List[str], new_lines: List[str], filename: str) -> List[Tuple[str, int, str]]:
        differ = difflib.Differ()
        diff = list(differ.compare(old_lines, new_lines))
        
        result = []
        old_line_num = 0
        new_line_num = 0
        
        i = 0
        while i < len(diff):
            line = diff[i]
            if line.startswith('+ '):
                new_line_num += 1
                result.append(('add', new_line_num, line[2:]))
            elif line.startswith('- '):
                old_line_num += 1
                result.append(('del', old_line_num, line[2:]))
            elif line.startswith('  '):
                old_line_num += 1
                new_line_num += 1
            elif line.startswith('? '):
                pass
            i += 1
        
        return result

    def generate_html(self, output_path: str):
        html = self._build_html()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _build_html(self) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diff Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .timestamp {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .section {{
            padding: 20px 30px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }}
        .file-list {{
            list-style: none;
        }}
        .file-item {{
            margin-bottom: 10px;
        }}
        details {{
            background: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 10px 15px;
            margin-bottom: 8px;
        }}
        summary {{
            cursor: pointer;
            font-weight: 500;
            color: #444;
            user-select: none;
            display: flex;
            align-items: center;
        }}
        summary:hover {{
            color: #667eea;
        }}
        summary::marker {{
            content: '▼ ';
        }}
        details[open] summary::marker {{
            content: '▲ ';
        }}
        .diff-content {{
            margin-top: 15px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            overflow-x: auto;
        }}
        .diff-line {{
            padding: 2px 5px;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .diff-add {{
            background: #e6ffec;
            color: #22863a;
            border-left: 3px solid #34d058;
        }}
        .diff-del {{
            background: #ffeef0;
            color: #d73a49;
            border-left: 3px solid #d73a49;
        }}
        .simple-file {{
            padding: 8px 12px;
            background: #f8f8f8;
            border-left: 3px solid #999;
            margin-bottom: 6px;
            border-radius: 2px;
            font-family: monospace;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }}
        .badge-add {{
            background: #d4edda;
            color: #155724;
        }}
        .badge-del {{
            background: #f8d7da;
            color: #721c24;
        }}
        .badge-mod {{
            background: #fff3cd;
            color: #856404;
        }}
        .no-changes {{
            color: #999;
            font-style: italic;
            padding: 10px 0;
        }}
        .dir-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 10px;
        }}
        .dir-column {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
        }}
        .dir-title {{
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        .file-entry {{
            font-family: monospace;
            font-size: 12px;
            padding: 4px 8px;
            background: #f9f9f9;
            border-left: 2px solid #ccc;
            margin-bottom: 4px;
        }}
        .file-added {{
            background: #d4edda;
            border-left: 2px solid #28a745;
        }}
        .file-deleted {{
            background: #f8d7da;
            border-left: 2px solid #dc3545;
        }}
        .file-modified {{
            background: #fff3cd;
            border-left: 2px solid #ffc107;
        }}
        .line-num {{
            display: inline-block;
            min-width: 40px;
            text-align: right;
            padding-right: 10px;
            color: #666;
            user-select: none;
            font-weight: 600;
        }}
        .search-container {{
            margin-top: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .search-input {{
            flex: 1;
            padding: 10px 15px;
            font-size: 14px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 4px;
            background: rgba(255,255,255,0.2);
            color: white;
            outline: none;
        }}
        .search-input::placeholder {{
            color: rgba(255,255,255,0.7);
        }}
        .search-input:focus {{
            border-color: rgba(255,255,255,0.6);
            background: rgba(255,255,255,0.3);
        }}
        .search-stats {{
            color: rgba(255,255,255,0.9);
            font-size: 13px;
        }}
        .highlight-match {{
            background: #ffeb3b !important;
            font-weight: 600;
        }}
        .file-hidden {{
            display: none !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ファイル差分レポート</h1>
            <div class="timestamp">生成日時: {timestamp}</div>
            <div class="timestamp">比較: {self.old_dir} ⇒ {self.new_dir}</div>
            <div class="search-container">
                <input type="text" class="search-input" id="searchInput" placeholder="ファイル内容で検索...">
                <span class="search-stats" id="searchStats"></span>
            </div>
        </header>
        <script>
        const searchInput = document.getElementById('searchInput');
        const searchStats = document.getElementById('searchStats');
        
        searchInput.addEventListener('input', function() {{
            const query = this.value.trim();
            
            // Remove previous highlights
            document.querySelectorAll('.highlight-match').forEach(el => {{
                el.classList.remove('highlight-match');
            }});
            
            if (query === '') {{
                // Show all files
                document.querySelectorAll('details').forEach(detail => {{
                    detail.classList.remove('file-hidden');
                }});
                searchStats.textContent = '';
                return;
            }}
            
            let matchedFiles = 0;
            let totalFiles = 0;
            
            // Search in all details elements (files)
            document.querySelectorAll('.section details').forEach(detail => {{
                totalFiles++;
                const content = detail.textContent.toLowerCase();
                const queryLower = query.toLowerCase();
                
                if (content.includes(queryLower)) {{
                    detail.classList.remove('file-hidden');
                    matchedFiles++;
                    
                    // Highlight matching lines
                    const diffLines = detail.querySelectorAll('.diff-line');
                    diffLines.forEach(line => {{
                        const lineText = line.textContent.toLowerCase();
                        if (lineText.includes(queryLower)) {{
                            line.classList.add('highlight-match');
                        }}
                    }});
                }} else {{
                    detail.classList.add('file-hidden');
                }}
            }});
            
            searchStats.textContent = `${{matchedFiles}} / ${{totalFiles}} ファイルがマッチ`;
        }});
        </script>
'''

        html += self._build_directory_section()
        html += self._build_added_section()
        html += self._build_deleted_section()
        html += self._build_modified_section()

        html += '''
    </div>
</body>
</html>
'''
        return html

    def _build_directory_section(self) -> str:
        modified_set = {file for file, _ in self.modified_files}
        added_set = set(self.added_files)
        deleted_set = set(self.deleted_files)
        
        section = '<div class="section"><h2 class="section-title">ディレクトリ一覧</h2>'
        section += '<details><summary>ファイル一覧を表示</summary>'
        section += '<div class="dir-grid">'
        
        section += '<div class="dir-column">'
        section += f'<div class="dir-title">Old: {self.old_dir}</div>'
        for file in self.old_all_files:
            if file in deleted_set:
                css_class = 'file-entry file-deleted'
            elif file in modified_set:
                css_class = 'file-entry file-modified'
            else:
                css_class = 'file-entry'
            section += f'<div class="{css_class}">{file}</div>'
        section += '</div>'
        
        section += '<div class="dir-column">'
        section += f'<div class="dir-title">New: {self.new_dir}</div>'
        for file in self.new_all_files:
            if file in added_set:
                css_class = 'file-entry file-added'
            elif file in modified_set:
                css_class = 'file-entry file-modified'
            else:
                css_class = 'file-entry'
            section += f'<div class="{css_class}">{file}</div>'
        section += '</div>'
        
        section += '</div></details></div>'
        return section

    def _build_added_section(self) -> str:
        section = '<div class="section"><h2 class="section-title">新規追加ファイル'
        section += f'<span class="badge badge-add">{len(self.added_files)}</span></h2>'
        
        if self.added_files:
            for file in self.added_files:
                section += '<details><summary>' + file + '</summary>'
                section += '<div class="diff-content">'
                
                file_path = self.new_file_paths[file]
                content = self._read_file(file_path)
                
                for line_num, line in enumerate(content, 1):
                    section += f'<div class="diff-line diff-add"><span class="line-num">{line_num}</span>+ {self._escape_html(line)}</div>'
                
                section += '</div></details>'
        else:
            section += '<div class="no-changes">新規ファイルはありません</div>'
        
        section += '</div>'
        return section

    def _build_deleted_section(self) -> str:
        section = '<div class="section"><h2 class="section-title">削除ファイル'
        section += f'<span class="badge badge-del">{len(self.deleted_files)}</span></h2>'
        
        if self.deleted_files:
            for file in self.deleted_files:
                section += '<details><summary>' + file + '</summary>'
                section += '<div class="diff-content">'
                
                file_path = self.old_file_paths[file]
                content = self._read_file(file_path)
                
                for line_num, line in enumerate(content, 1):
                    section += f'<div class="diff-line diff-del"><span class="line-num">{line_num}</span>- {self._escape_html(line)}</div>'
                
                section += '</div></details>'
        else:
            section += '<div class="no-changes">削除ファイルはありません</div>'
        
        section += '</div>'
        return section

    def _build_modified_section(self) -> str:
        section = '<div class="section"><h2 class="section-title">変更ファイル'
        section += f'<span class="badge badge-mod">{len(self.modified_files)}</span></h2>'
        
        if self.modified_files:
            for file, diff in self.modified_files:
                section += '<details><summary>' + file + '</summary>'
                section += '<div class="diff-content">'
                
                for change_type, line_num, line in diff:
                    if change_type == 'add':
                        section += f'<div class="diff-line diff-add"><span class="line-num">{line_num}</span>+ {self._escape_html(line)}</div>'
                    elif change_type == 'del':
                        section += f'<div class="diff-line diff-del"><span class="line-num">{line_num}</span>- {self._escape_html(line)}</div>'
                
                section += '</div></details>'
        else:
            section += '<div class="no-changes">変更ファイルはありません</div>'
        
        section += '</div>'
        return section

    def _escape_html(self, text: str) -> str:
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    parser = argparse.ArgumentParser(description='ディレクトリ間のファイル差分を検出し、HTML レポートを生成します')
    parser.add_argument('old_dir', help='比較元ディレクトリ')
    parser.add_argument('new_dir', help='比較先ディレクトリ')
    parser.add_argument('-o', '--output', default='diff_report.html', help='出力HTMLファイル名（デフォルト: diff_report.html）')
    parser.add_argument('-e', '--extensions', nargs='+', default=['.php'], help='対象ファイル拡張子（デフォルト: .php）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.old_dir):
        print(f"エラー: ディレクトリ '{args.old_dir}' が存在しません", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(args.new_dir):
        print(f"エラー: ディレクトリ '{args.new_dir}' が存在しません", file=sys.stderr)
        sys.exit(1)
    
    print(f"ディレクトリをスキャン中...")
    report = DiffReport(args.old_dir, args.new_dir, args.extensions)
    report.scan_directories()
    
    print(f"差分を生成中...")
    report.generate_html(args.output)
    
    print(f"\n完了:")
    print(f"  新規ファイル: {len(report.added_files)}")
    print(f"  削除ファイル: {len(report.deleted_files)}")
    print(f"  変更ファイル: {len(report.modified_files)}")
    print(f"\nレポート: {args.output}")


if __name__ == '__main__':
    main()
