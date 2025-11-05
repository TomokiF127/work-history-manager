@echo off
REM 職務経歴管理ツール セットアップスクリプト（Windows用）

echo ================================================
echo   職務経歴管理ツール セットアップ
echo ================================================
echo.

REM スクリプトのディレクトリに移動
cd /d "%~dp0"

REM 1. Python仮想環境の作成
echo ✓ Python仮想環境を作成中...
if not exist "venv" (
    python -m venv venv
    echo   仮想環境を作成しました
) else (
    echo   仮想環境は既に存在します
)

REM 2. 仮想環境の有効化
echo.
echo ✓ 仮想環境を有効化中...
call venv\Scripts\activate.bat

REM 3. pipのアップグレード
echo.
echo ✓ pipをアップグレード中...
python -m pip install --upgrade pip >nul 2>&1

REM 4. 依存パッケージのインストール
echo.
echo ✓ 依存パッケージをインストール中...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo   依存パッケージをインストールしました
) else (
    echo   ⚠ requirements.txtが見つかりません
)

REM 5. 設定ファイルの作成
echo.
echo ✓ 設定ファイルを作成中...
if not exist "config.ini" (
    if exist "config.ini.sample" (
        copy config.ini.sample config.ini >nul
        echo   config.iniを作成しました
    ) else (
        echo   ⚠ config.ini.sampleが見つかりません
    )
) else (
    echo   config.iniは既に存在します
)

echo.
echo ================================================
echo   セットアップが完了しました！
echo ================================================
echo.
echo 次のステップ：
echo   1. '起動.bat' をダブルクリックしてアプリを起動
echo   または
echo   2. コマンドプロンプトで以下を実行：
echo      venv\Scripts\activate
echo      python app\main.py
echo.
pause
