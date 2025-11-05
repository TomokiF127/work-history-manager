#!/bin/bash
# 職務経歴管理ツール セットアップスクリプト（macOS/Linux用）

set -e  # エラーが発生したら即座に終了

echo "================================================"
echo "  職務経歴管理ツール セットアップ"
echo "================================================"
echo ""

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 1. Python仮想環境の作成
echo "✓ Python仮想環境を作成中..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  仮想環境を作成しました"
else
    echo "  仮想環境は既に存在します"
fi

# 2. 仮想環境の有効化
echo ""
echo "✓ 仮想環境を有効化中..."
source venv/bin/activate

# 3. pipのアップグレード
echo ""
echo "✓ pipをアップグレード中..."
pip install --upgrade pip > /dev/null 2>&1

# 4. 依存パッケージのインストール
echo ""
echo "✓ 依存パッケージをインストール中..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "  依存パッケージをインストールしました"
else
    echo "  ⚠ requirements.txtが見つかりません"
fi

# 5. 設定ファイルの作成
echo ""
echo "✓ 設定ファイルを作成中..."
if [ ! -f "config.ini" ] && [ -f "config.ini.sample" ]; then
    cp config.ini.sample config.ini
    echo "  config.iniを作成しました"
elif [ -f "config.ini" ]; then
    echo "  config.iniは既に存在します"
else
    echo "  ⚠ config.ini.sampleが見つかりません"
fi

# 6. 起動スクリプトに実行権限を付与
echo ""
echo "✓ 起動スクリプトに実行権限を付与中..."
if [ -f "起動.command" ]; then
    chmod +x 起動.command
    # Quarantine属性を削除（macOSのセキュリティ警告を回避）
    xattr -d com.apple.quarantine 起動.command 2>/dev/null || true
    echo "  起動.commandに実行権限を付与しました"
fi

echo ""
echo "================================================"
echo "  セットアップが完了しました！"
echo "================================================"
echo ""
echo "次のステップ："
echo "  1. '起動.command' をダブルクリックしてアプリを起動"
echo "  または"
echo "  2. ターミナルで以下を実行："
echo "     source venv/bin/activate"
echo "     python app/main.py"
echo ""
