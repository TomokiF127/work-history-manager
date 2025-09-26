#!/bin/bash
# 職務経歴管理ツール起動スクリプト

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境をアクティベート
source venv/bin/activate

# アプリケーションを起動
python app/main.py