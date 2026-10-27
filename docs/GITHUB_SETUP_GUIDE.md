# GitHub Repository Structure

## ディレクトリ構造

```
comprehensive-debug-framework/
├── README.md                          # プロジェクト概要・クイックスタート
├── LICENSE                            # MIT ライセンス
├── setup.py                          # パッケージ設定
├── requirements.txt                  # 依存関係（なし）
├── MANIFEST.in                       # パッケージ含含ファイル定義
├── .gitignore                        # Git無視ファイル設定
│
├── debug_framework/                  # メインパッケージ
│   ├── __init__.py                  # パッケージ初期化
│   ├── exception_handler.py          # SafeExceptionHandler
│   ├── memory_management.py          # ProcessHookManager
│   ├── retry_manager.py              # AdaptiveRetryManager
│   ├── frequency_control.py          # 周波数制御関連
│   ├── error_logging.py              # RingBufferErrorHook
│   └── system.py                     # RobustProcessingSystem (統合)
│
├── tests/                            # テストスイート
│   ├── __init__.py
│   └── test_basic.py                 # 単体テスト
│
├── docs/                             # ドキュメント
│   ├── ARCHITECTURE.md               # システムアーキテクチャ
│   └── TROUBLESHOOTING.md            # トラブルシューティング
│
└── examples/                         # 使用例
    └── basic_usage.py                # 8つの基本的な使用例
```

## 各ファイルの説明

### ルートレベル

| ファイル | 説明 | 行数 |
|---------|------|------|
| README.md | プロジェクト概要、インストール、クイックスタート | ~400 |
| LICENSE | MIT ライセンス | ~22 |
| setup.py | PyPI パッケージ設定 | ~40 |
| requirements.txt | 依存関係（なし） | ~1 |
| MANIFEST.in | パッケージ含含ファイル定義 | ~5 |
| .gitignore | Git無視ファイル設定 | ~50 |

### debug_framework/ パッケージ

| ファイル | コンポーネント | 説明 | 行数 |
|---------|--------------|------|------|
| __init__.py | - | 全コンポーネントのエクスポート | ~30 |
| exception_handler.py | SafeExceptionHandler | 例外処理の安全性保証 | ~60 |
| memory_management.py | ProcessHookManager | メモリ連動処理管理 | ~90 |
| retry_manager.py | AdaptiveRetryManager | 適応的リトライ管理 | ~80 |
| frequency_control.py | 周波数制御 | 周波数適応型削減 + サーキットブレーカー | ~150 |
| error_logging.py | RingBufferErrorHook | エラーログ循環バッファ | ~60 |
| system.py | RobustProcessingSystem | 統合システム | ~120 |
| **合計** | - | - | **~590** |

### tests/

| ファイル | 説明 | テスト数 |
|---------|------|---------|
| test_basic.py | 各コンポーネントの単体テスト | 15+ |

### docs/

| ファイル | 説明 | 内容 |
|---------|------|------|
| ARCHITECTURE.md | システムアーキテクチャ | 詳細なアーキテクチャ、処理フロー、拡張ポイント |
| TROUBLESHOOTING.md | トラブルシューティング | よくある問題の解決方法、デバッグテクニック |

### examples/

| ファイル | 説明 | 例数 |
|---------|------|------|
| basic_usage.py | 基本的な使用例 | 8つの実装例 |

## インストール方法

### pip からインストール（予定）

```bash
pip install comprehensive-debug-framework
```

### 手動インストール

```bash
git clone https://github.com/yourusername/comprehensive-debug-framework.git
cd comprehensive-debug-framework
pip install -e .
```

## 推奨される読む順序

### ユーザー向け

1. `README.md` - プロジェクト概要
2. `examples/basic_usage.py` - 実装例を実行
3. `docs/TROUBLESHOOTING.md` - 問題解決方法

### 開発者向け

1. `README.md` - プロジェクト概要
2. `docs/ARCHITECTURE.md` - システムアーキテクチャ
3. `debug_framework/*.py` - ソースコード
4. `tests/test_basic.py` - テストコード

## ファイル総数とサイズ

```
Python ファイル: 12 (実装 7 + テスト 1 + 例 1 + その他 3)
ドキュメント: 2 (+ README 1)
設定ファイル: 6 (.gitignore, setup.py, requirements.txt, LICENSE, MANIFEST.in, __init__.py)
合計: 21 ファイル

推定総行数: 1500+ 行
```

## 必須ファイルと推奨ファイル

### 必須（GitHub に上げる）

- ✓ `debug_framework/` ディレクトリ全体
- ✓ `tests/` ディレクトリ全体
- ✓ `README.md`
- ✓ `LICENSE`
- ✓ `setup.py`
- ✓ `.gitignore`

### 推奨（ユーザー体験向上）

- ✓ `docs/ARCHITECTURE.md`
- ✓ `docs/TROUBLESHOOTING.md`
- ✓ `examples/basic_usage.py`
- ✓ `requirements.txt`
- ✓ `MANIFEST.in`

### オプション（将来）

- `.github/workflows/` - CI/CD パイプライン
- `tox.ini` - 複数環境テスト
- `docs/API_REFERENCE.md` - API リファレンス

## GitHub リポジトリの初期セットアップ

```bash
# リポジトリを初期化
git init
git add .
git commit -m "Initial commit: Comprehensive Debug Framework v1.0.0"

# リモートを追加
git remote add origin https://github.com/yourusername/comprehensive-debug-framework.git

# メインブランチにプッシュ
git branch -M main
git push -u origin main

# タグを作成
git tag v1.0.0
git push origin v1.0.0
```

## PyPI に公開するまでの手順

```bash
# ビルド
python setup.py sdist bdist_wheel

# テスト環境に上げる
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 本番環境に上げる
twine upload dist/*
```

## チェックリスト

- [ ] すべてのファイルが `comprehensive-debug-framework/` に配置されている
- [ ] `README.md` が正しく記述されている
- [ ] `LICENSE` が含まれている（MIT ライセンス）
- [ ] `setup.py` に正しいメタデータが含まれている
- [ ] テストが実行可能である
- [ ] 例が実行可能である
- [ ] `.gitignore` が正しく設定されている
- [ ] ドキュメントが完全である

---

**準備完了日**: 2026-05-26
**フレームワークバージョン**: 1.0.0
**ステータス**: Production Ready ✓
