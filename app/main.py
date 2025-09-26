#!/usr/bin/env python3
import sys
import os
import locale
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QLocale
from ui.main_window import MainWindow
from services.db import db_service
from services.seed import seed_initial_data

def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    # 設定ファイルを読み込み
    from config import config
    
    app = QApplication(sys.argv)
    app.setApplicationName(config.get_app_name())
    app.setOrganizationName("WorkHistory")
    
    # 日本語ロケールを設定
    try:
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Japanese_Japan.932')
        except:
            pass
    
    # Qtロケールを日本語に設定
    QLocale.setDefault(QLocale(QLocale.Language.Japanese, QLocale.Country.Japan))
    
    # データベースディレクトリは models/base.py で自動作成される
    
    # 初期データ投入（設定ファイルで制御）
    if config.should_seed_initial_data():
        try:
            with db_service.session_scope() as session:
                seed_initial_data(session)
        except Exception as e:
            print(f"初期データ投入エラー: {e}")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()