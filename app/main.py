#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from services.db import db_service
from services.seed import seed_initial_data

def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    app = QApplication(sys.argv)
    app.setApplicationName("職務経歴管理ツール")
    app.setOrganizationName("WorkHistory")
    
    os.makedirs("./data", exist_ok=True)
    
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