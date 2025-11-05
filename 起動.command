#!/bin/bash
# 職務経歴管理ツール起動スクリプト

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# ========================================
# 初回セットアップチェック
# ========================================

# 仮想環境が存在しない場合は初回セットアップを実行
if [ ! -d "venv" ]; then
    echo "================================================"
    echo "  初回起動を検出しました"
    echo "================================================"
    echo ""
    echo "このアプリケーションを実行するには、初回のみセットアップが必要です。"
    echo ""
    echo "セットアップ内容："
    echo "  1. Python仮想環境の作成"
    echo "  2. 依存パッケージのインストール（数分かかります）"
    echo "  3. 設定ファイルの作成"
    echo ""
    echo "※ セットアップは1度だけ実行すれば、2回目以降は不要です"
    echo ""
    read -p "セットアップを開始してもよろしいですか？ (y/n): " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "セットアップをスキップしました。"
        echo ""
        echo "アプリを使用するには、後でもう一度このファイルを実行して"
        echo "セットアップを完了してください。"
        echo ""
        read -p "Enterキーを押して終了..."
        exit 1
    fi

    echo ""
    echo "========================================="
    echo "  セットアップを開始します..."
    echo "========================================="
    echo ""

    # Python3が利用可能かチェック
    if ! command -v python3 &> /dev/null; then
        echo "❌ エラー: Python 3がインストールされていません。"
        echo ""
        echo "Python 3のインストール方法："
        echo "  1. https://www.python.org/downloads/ からダウンロード"
        echo "  2. Homebrewを使用: brew install python3"
        echo ""
        read -p "Enterキーを押して終了..."
        exit 1
    fi

    # 1. Python仮想環境の作成
    echo "✓ [1/4] Python仮想環境を作成中..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "  ✅ 仮想環境を作成しました"
    else
        echo "  ❌ 仮想環境の作成に失敗しました"
        read -p "Enterキーを押して終了..."
        exit 1
    fi

    # 2. 仮想環境の有効化
    echo ""
    echo "✓ [2/4] 仮想環境を有効化中..."
    source venv/bin/activate

    # 3. pipのアップグレード
    echo ""
    echo "✓ [3/4] pipをアップグレード中..."
    pip install --upgrade pip > /dev/null 2>&1

    # 4. 依存パッケージのインストール
    echo ""
    echo "✓ [4/4] 依存パッケージをインストール中..."
    echo "  (この処理には数分かかる場合があります)"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            echo "  ✅ 依存パッケージをインストールしました"
        else
            echo "  ❌ 依存パッケージのインストールに失敗しました"
            read -p "Enterキーを押して終了..."
            exit 1
        fi
    else
        echo "  ❌ requirements.txtが見つかりません"
        read -p "Enterキーを押して終了..."
        exit 1
    fi

    # 設定ファイルの作成
    echo ""
    if [ ! -f "config.ini" ] && [ -f "config.ini.sample" ]; then
        cp config.ini.sample config.ini
        echo "✅ config.iniを作成しました"
    fi

    echo ""
    echo "================================================"
    echo "  ✅ セットアップが完了しました！"
    echo "================================================"
    echo ""
    echo "アプリケーションを起動します..."
    sleep 2
else
    # 既存の仮想環境をアクティベート
    source venv/bin/activate
fi

# ========================================
# アプリケーションを起動
# ========================================
python app/main.py

# エラーコードをチェック
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ アプリケーションの起動に失敗しました。"
    echo ""
    read -p "Enterキーを押して終了..."
fi