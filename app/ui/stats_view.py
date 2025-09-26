from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableView, QPushButton, QLabel, QDateEdit,
    QGroupBox, QMessageBox, QFileDialog, QHeaderView
)
from PySide6.QtCore import Qt, QDate, Signal, QAbstractTableModel, QModelIndex
from datetime import date
import os
from typing import List, Optional
from services.db import db_service
from services.stats import StatsService
from services.export import ExportService
from services.repository import Repository

class StatsTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self.stats_data = data or []
        self.headers = ["技術名", "月数", "年月"]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.stats_data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        item = self.stats_data[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:
                return item['name']
            elif col == 1:
                return str(item['months'])
            elif col == 2:
                return item['display']
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def update_data(self, data):
        self.beginResetModel()
        self.stats_data = data
        self.endResetModel()

class CategoryStatsTab(QWidget):
    def __init__(self, kind, title):
        super().__init__()
        self.kind = kind
        self.title = title
        self.start_filter = None
        self.end_filter = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.summary_label = QLabel("統計データ")
        layout.addWidget(self.summary_label)
        
        self.table_view = QTableView()
        self.model = StatsTableModel()
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setAlternatingRowColors(True)
        layout.addWidget(self.table_view)
        
        export_layout = QHBoxLayout()
        
        self.export_csv_button = QPushButton("CSVエクスポート")
        self.export_csv_button.clicked.connect(self.export_csv)
        export_layout.addWidget(self.export_csv_button)
        
        self.export_md_button = QPushButton("Markdownエクスポート")
        self.export_md_button.clicked.connect(self.export_md)
        export_layout.addWidget(self.export_md_button)
        
        export_layout.addStretch()
        layout.addLayout(export_layout)
    
    def refresh_stats(self, start_filter=None, end_filter=None):
        self.start_filter = start_filter
        self.end_filter = end_filter
        
        try:
            with db_service.session_scope() as session:
                stats_service = StatsService(session)
                stats_data = stats_service.get_all_tech_stats(
                    self.kind, start_filter, end_filter
                )
                self.model.update_data(stats_data)
                
                total_techs = len(stats_data)
                total_months = sum(item['months'] for item in stats_data)
                
                period_text = ""
                if start_filter or end_filter:
                    if start_filter and end_filter:
                        period_text = f" (期間: {start_filter} ~ {end_filter})"
                    elif start_filter:
                        period_text = f" (期間: {start_filter} ~)"
                    else:
                        period_text = f" (期間: ~ {end_filter})"
                
                self.summary_label.setText(
                    f"{self.title}: {total_techs}件 / 合計{total_months}ヶ月{period_text}"
                )
        except Exception as e:
            print(f"統計データ取得エラー: {e}")
            self.model.update_data([])
            self.summary_label.setText(f"{self.title}: データなし")
    
    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"{self.title}をCSVエクスポート",
            f"{self.kind}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            with db_service.session_scope() as session:
                export_service = ExportService(session)
                success = export_service.export_category_csv(
                    self.kind, file_path, self.start_filter, self.end_filter
                )
                
                if success:
                    QMessageBox.information(
                        self, "成功",
                        f"CSVファイルをエクスポートしました:\n{file_path}"
                    )
                else:
                    QMessageBox.critical(
                        self, "エラー",
                        "CSVエクスポートに失敗しました"
                    )
    
    def export_md(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"{self.title}をMarkdownエクスポート",
            f"{self.kind}.md",
            "Markdown Files (*.md)"
        )
        
        if file_path:
            with db_service.session_scope() as session:
                export_service = ExportService(session)
                success = export_service.export_category_md(
                    self.kind, file_path, self.start_filter, self.end_filter
                )
                
                if success:
                    QMessageBox.information(
                        self, "成功",
                        f"Markdownファイルをエクスポートしました:\n{file_path}"
                    )
                else:
                    QMessageBox.critical(
                        self, "エラー",
                        "Markdownエクスポートに失敗しました"
                    )

class StatsView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.set_default_filters()
        # デフォルトフィルタの値で統計を表示
        self.apply_filter()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        filter_group = QGroupBox("集計期間フィルタ")
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("開始:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setSpecialValueText("指定なし")
        self.start_date.setDisplayFormat("yyyy年MM月dd日")
        filter_layout.addWidget(self.start_date)
        
        filter_layout.addWidget(QLabel("終了:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setSpecialValueText("指定なし")
        self.end_date.setDisplayFormat("yyyy年MM月dd日")
        filter_layout.addWidget(self.end_date)
        
        self.apply_filter_button = QPushButton("フィルタ適用")
        self.apply_filter_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.apply_filter_button)
        
        self.clear_filter_button = QPushButton("クリア")
        self.clear_filter_button.clicked.connect(self.clear_filter)
        filter_layout.addWidget(self.clear_filter_button)
        
        filter_layout.addStretch()
        
        self.export_all_button = QPushButton("全カテゴリ一括エクスポート")
        self.export_all_button.clicked.connect(self.export_all)
        filter_layout.addWidget(self.export_all_button)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        self.summary_group = QGroupBox("サマリー")
        summary_layout = QHBoxLayout()
        self.summary_label = QLabel("統計サマリー")
        summary_layout.addWidget(self.summary_label)
        self.summary_group.setLayout(summary_layout)
        layout.addWidget(self.summary_group)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        categories = [
            ('os', 'OS'),
            ('language', '言語'),
            ('framework', 'フレームワーク'),
            ('tool', 'ツール'),
            ('cloud', 'クラウド'),
            ('db', 'データベース')
        ]
        
        self.category_tabs = {}
        for kind, title in categories:
            tab = CategoryStatsTab(kind, title)
            self.category_tabs[kind] = tab
            self.tab_widget.addTab(tab, title)
    
    def apply_filter(self):
        start_filter = None
        end_filter = None
        
        if self.start_date.date() != self.start_date.minimumDate():
            start_filter = self.start_date.date().toString("yyyy-MM-dd")
        
        if self.end_date.date() != self.end_date.minimumDate():
            end_filter = self.end_date.date().toString("yyyy-MM-dd")
        
        self.refresh_stats(start_filter, end_filter)
    
    def clear_filter(self):
        self.start_date.setDate(self.start_date.minimumDate())
        self.end_date.setDate(self.end_date.minimumDate())
        self.refresh_stats()
    
    def set_default_filters(self):
        """デフォルトのフィルタを設定（全期間）"""
        try:
            from services.db import db_service
            from services.repository import Repository
            
            with db_service.session_scope() as session:
                repo = Repository(session)
                projects = repo.get_all_projects()
                
                if projects:
                    # 最も古い開始日を探す
                    oldest_date = None
                    for project in projects:
                        if project.project_start:
                            project_date = QDate.fromString(project.project_start, "yyyy-MM-dd")
                            if project_date.isValid():
                                if oldest_date is None or project_date < oldest_date:
                                    oldest_date = project_date
                    
                    # デフォルト値を設定（全期間）
                    if oldest_date:
                        self.start_date.setDate(oldest_date)
                    else:
                        self.start_date.setDate(QDate.currentDate().addYears(-10))
                    
                    self.end_date.setDate(QDate.currentDate())
                else:
                    # プロジェクトがない場合（何も指定しない）
                    pass
        except Exception as e:
            print(f"統計フィルタ設定エラー: {e}")
    
    def refresh_stats(self, start_filter=None, end_filter=None):
        try:
            for tab in self.category_tabs.values():
                tab.refresh_stats(start_filter, end_filter)
        except Exception as e:
            print(f"統計更新エラー: {e}")
        
        with db_service.session_scope() as session:
            stats_service = StatsService(session)
            summary = stats_service.get_summary_stats(start_filter, end_filter)
            
            period_text = ""
            if start_filter or end_filter:
                if start_filter and end_filter:
                    period_text = f" | 期間: {start_filter} ~ {end_filter}"
                elif start_filter:
                    period_text = f" | 期間: {start_filter} ~ 現在"
                else:
                    period_text = f" | 期間: 開始 ~ {end_filter}"
            
            tech_summary = []
            for cat, count in summary['tech_counts'].items():
                if count > 0:
                    cat_names = {
                        'os': 'OS', 'language': '言語',
                        'framework': 'FW', 'tool': 'ツール',
                        'cloud': 'クラウド', 'db': 'DB'
                    }
                    tech_summary.append(f"{cat_names[cat]}:{count}")
            
            self.summary_label.setText(
                f"プロジェクト数: {summary['total_projects']} | "
                f"総月数: {summary['total_months']}ヶ月 | "
                f"技術: {', '.join(tech_summary)}"
                f"{period_text}"
            )
    
    def export_all(self):
        directory = QFileDialog.getExistingDirectory(
            self, "エクスポート先フォルダを選択",
            "", QFileDialog.ShowDirsOnly
        )
        
        if directory:
            start_filter = None
            end_filter = None
            
            if self.start_date.date() != self.start_date.minimumDate():
                start_filter = self.start_date.date().toString("yyyy-MM-dd")
            
            if self.end_date.date() != self.end_date.minimumDate():
                end_filter = self.end_date.date().toString("yyyy-MM-dd")
            
            reply = QMessageBox.question(
                self, "エクスポート形式",
                "エクスポート形式を選択してください",
                "CSV", "Markdown", "両方"
            )
            
            with db_service.session_scope() as session:
                export_service = ExportService(session)
                
                success_count = 0
                total_count = 0
                
                if reply == 0 or reply == 2:
                    csv_results = export_service.export_all_categories_csv(
                        directory, start_filter, end_filter
                    )
                    for category, success in csv_results.items():
                        total_count += 1
                        if success:
                            success_count += 1
                
                if reply == 1 or reply == 2:
                    md_results = export_service.export_all_categories_md(
                        directory, start_filter, end_filter
                    )
                    for category, success in md_results.items():
                        total_count += 1
                        if success:
                            success_count += 1
                
                projects_csv = os.path.join(directory, "projects.csv")
                if export_service.export_projects_csv(
                    projects_csv, start_filter, end_filter
                ):
                    success_count += 1
                total_count += 1
                
                QMessageBox.information(
                    self, "エクスポート完了",
                    f"{success_count}/{total_count} ファイルを\n"
                    f"{directory}\nにエクスポートしました"
                )