@echo off
rem 職務経歴管理ツール起動バッチファイル

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo 仮想環境が見つかりません。
    echo 以下のコマンドを実行してセットアップしてください：
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python app\main.py

pause