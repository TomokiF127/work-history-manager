@echo off
rem 職務経歴管理ツール起動バッチファイル
chcp 65001 >nul
cd /d "%~dp0"

REM ========================================
REM 初回セットアップチェック
REM ========================================

if not exist "venv" (
    echo ================================================
    echo   初回起動を検出しました
    echo ================================================
    echo.
    echo このアプリケーションを実行するには、以下のセットアップが必要です：
    echo   1. Python仮想環境の作成
    echo   2. 依存パッケージのインストール
    echo   3. 設定ファイルの作成
    echo.
    set /p CONFIRM="セットアップを開始してもよろしいですか？ (y/n): "

    if /i not "%CONFIRM%"=="y" (
        echo.
        echo セットアップがキャンセルされました。
        echo 後でセットアップする場合は、再度このファイルを実行してください。
        pause
        exit /b 1
    )

    echo.
    echo =========================================
    echo   セットアップを開始します...
    echo =========================================
    echo.

    REM Pythonが利用可能かチェック
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ エラー: Pythonがインストールされていません。
        echo.
        echo Pythonのインストール方法：
        echo   https://www.python.org/downloads/ からダウンロードしてインストール
        echo.
        pause
        exit /b 1
    )

    REM 1. Python仮想環境の作成
    echo ✓ [1/4] Python仮想環境を作成中...
    python -m venv venv
    if errorlevel 1 (
        echo   ❌ 仮想環境の作成に失敗しました
        pause
        exit /b 1
    )
    echo   ✅ 仮想環境を作成しました

    REM 2. 仮想環境の有効化
    echo.
    echo ✓ [2/4] 仮想環境を有効化中...
    call venv\Scripts\activate.bat

    REM 3. pipのアップグレード
    echo.
    echo ✓ [3/4] pipをアップグレード中...
    python -m pip install --upgrade pip >nul 2>&1

    REM 4. 依存パッケージのインストール
    echo.
    echo ✓ [4/4] 依存パッケージをインストール中...
    echo   (この処理には数分かかる場合があります)
    if exist "requirements.txt" (
        pip install -r requirements.txt
        if errorlevel 1 (
            echo   ❌ 依存パッケージのインストールに失敗しました
            pause
            exit /b 1
        )
        echo   ✅ 依存パッケージをインストールしました
    ) else (
        echo   ❌ requirements.txtが見つかりません
        pause
        exit /b 1
    )

    REM 設定ファイルの作成
    echo.
    if not exist "config.ini" (
        if exist "config.ini.sample" (
            copy config.ini.sample config.ini >nul
            echo ✅ config.iniを作成しました
        )
    )

    echo.
    echo ================================================
    echo   ✅ セットアップが完了しました！
    echo ================================================
    echo.
    echo アプリケーションを起動します...
    timeout /t 2 >nul
) else (
    REM 既存の仮想環境をアクティベート
    call venv\Scripts\activate.bat
)

REM ========================================
REM アプリケーションを起動
REM ========================================
python app\main.py

REM エラーコードをチェック
if errorlevel 1 (
    echo.
    echo ❌ アプリケーションの起動に失敗しました。
    echo.
)

pause