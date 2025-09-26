#!/bin/bash
# 単一実行ファイル作成スクリプト

echo "職務経歴管理ツール - 実行ファイル作成"
echo "================================"

# 仮想環境をアクティベート
source venv/bin/activate

# PyInstallerをインストール（未インストールの場合）
pip install pyinstaller

echo "実行ファイルを作成中..."

# 実行ファイルを作成
pyinstaller \
  --onefile \
  --windowed \
  --name "職務経歴管理ツール" \
  --add-data "app/data:data" \
  --hidden-import="sqlalchemy.sql.default_comparator" \
  --hidden-import="PySide6.QtCore" \
  --hidden-import="PySide6.QtWidgets" \
  --hidden-import="PySide6.QtGui" \
  app/main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 実行ファイルが作成されました！"
    echo "場所: dist/職務経歴管理ツール"
    echo ""
    echo "この実行ファイルをダブルクリックしてアプリを起動できます。"
else
    echo "❌ 実行ファイルの作成に失敗しました。"
fi