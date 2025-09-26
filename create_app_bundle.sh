#!/bin/bash
# macOS用アプリケーションバンドル作成スクリプト

echo "職務経歴管理ツール - macOSアプリ作成"
echo "================================"

APP_NAME="職務経歴管理ツール"
BUNDLE_NAME="${APP_NAME}.app"

# 仮想環境をアクティベート
source venv/bin/activate

# PyInstallerをインストール（未インストールの場合）
pip install pyinstaller

echo "macOSアプリケーションを作成中..."

# macOS用アプリケーションバンドルを作成
pyinstaller \
  --onedir \
  --windowed \
  --name "${APP_NAME}" \
  --add-data "app/data:data" \
  --hidden-import="sqlalchemy.sql.default_comparator" \
  --hidden-import="PySide6.QtCore" \
  --hidden-import="PySide6.QtWidgets" \
  --hidden-import="PySide6.QtGui" \
  --osx-bundle-identifier="com.workhistory.app" \
  app/main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ macOSアプリケーションが作成されました！"
    echo "場所: dist/${BUNDLE_NAME}"
    echo ""
    echo "Finderで「dist」フォルダを開き、「${APP_NAME}.app」をダブルクリックして起動できます。"
    echo "アプリケーションフォルダにコピーして使用することも可能です。"
    
    # Finderで開く
    open dist/
else
    echo "❌ アプリケーションの作成に失敗しました。"
fi