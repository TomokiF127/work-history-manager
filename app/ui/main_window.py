from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QMessageBox, QStatusBar,
    QFileDialog, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from ui.projects_view import ProjectsView
from ui.masters_view import MastersView
from ui.stats_view import StatsView
from ui.self_pr_view import SelfPRView
from services.skill_sheet_export import SkillSheetExportService
from services.db import db_service

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        from config import config
        
        self.setWindowTitle(config.get_app_name())
        width, height = config.get_window_size()
        self.setGeometry(100, 100, width, height)
        
        self.init_ui()
        self.init_menu()
        self.init_statusbar()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        self.projects_view = ProjectsView()
        self.tab_widget.addTab(self.projects_view, "プロジェクト管理")
        
        self.masters_view = MastersView()
        self.tab_widget.addTab(self.masters_view, "マスタ管理")
        
        self.stats_view = StatsView()
        self.tab_widget.addTab(self.stats_view, "経験年数統計")
        
        self.self_pr_view = SelfPRView()
        self.tab_widget.addTab(self.self_pr_view, "自己PR管理")
        
        self.projects_view.data_changed.connect(self.on_data_changed)
        self.masters_view.data_changed.connect(self.on_data_changed)
        self.self_pr_view.data_changed.connect(self.on_data_changed)
    
    def init_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("ファイル(&F)")
        
        export_action = file_menu.addAction("統計をエクスポート(&E)")
        export_action.triggered.connect(self.stats_view.export_all)
        
        skill_sheet_action = file_menu.addAction("スキルシートをエクスポート(&S)")
        skill_sheet_action.triggered.connect(self.export_skill_sheet)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("終了(&X)")
        exit_action.triggered.connect(self.close)
        
        help_menu = menubar.addMenu("ヘルプ(&H)")
        
        about_action = help_menu.addAction("このアプリについて(&A)")
        about_action.triggered.connect(self.show_about)
    
    def init_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("準備完了")
    
    def on_data_changed(self):
        self.projects_view.refresh_data()
        self.stats_view.refresh_stats()
        self.status_bar.showMessage("データが更新されました", 3000)
    
    def show_about(self):
        QMessageBox.information(
            self,
            "職務経歴管理ツールについて",
            "職務経歴管理ツール v1.5.0\n\n"
            "プロジェクトと技術経験を管理し、\n"
            "重複なしで経験月数を集計するツールです。\n\n"
            "© 2024 TomokiF127"
        )
    
    def export_skill_sheet(self):
        """スキルシートをエクスポート"""
        # 名前を入力
        name, ok = QInputDialog.getText(
            self, "氏名入力", 
            "スキルシートに記載する氏名を入力してください:",
            text="氏名"
        )
        
        if not ok:
            return
        
        # 出力形式を選択
        formats = ["Word文書 (*.docx)", "Markdown (*.md)"]
        format_choice = QMessageBox.question(
            self, "出力形式選択",
            "出力形式を選択してください。\n\nWord文書: スキルシートのフォーマットで出力\nMarkdown: テキスト形式で出力",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        
        if format_choice == QMessageBox.StandardButton.Cancel:
            return
        
        # ファイル保存ダイアログ
        file_filter = "Word文書 (*.docx);;Markdown (*.md)"
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "スキルシートを保存", 
            f"スキルシート_{name}.docx",
            file_filter
        )
        
        if not filepath:
            return
        
        try:
            with db_service.session_scope() as session:
                export_service = SkillSheetExportService(session)
                
                if selected_filter == "Markdown (*.md)" or filepath.endswith(".md"):
                    if not filepath.endswith(".md"):
                        filepath += ".md"
                    export_service.export_to_markdown(filepath, name)
                    QMessageBox.information(
                        self, "成功", 
                        f"スキルシートをMarkdown形式で保存しました:\n{filepath}"
                    )
                else:
                    if not filepath.endswith(".docx"):
                        filepath += ".docx"
                    export_service.export_to_docx(filepath, name)
                    QMessageBox.information(
                        self, "成功", 
                        f"スキルシートをWord文書として保存しました:\n{filepath}"
                    )
                    
        except Exception as e:
            QMessageBox.critical(
                self, "エラー",
                f"スキルシートの出力中にエラーが発生しました:\n{str(e)}"
            )