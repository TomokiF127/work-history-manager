from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTableView, QPushButton, QLineEdit, QComboBox,
    QLabel, QGroupBox, QDateEdit, QMessageBox,
    QTabWidget, QTextEdit, QListWidget, QListWidgetItem,
    QAbstractItemView, QHeaderView, QDialog, QDialogButtonBox,
    QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt, QDate, Signal, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from datetime import date, datetime
from typing import List, Optional
from services.db import db_service
from services.repository import Repository

class ProjectTableModel(QAbstractTableModel):
    def __init__(self, projects=None):
        super().__init__()
        self.projects = []
        self.headers = ["プロジェクト名", "役割", "期間", "規模"]
        if projects:
            self.update_projects(projects)
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.projects)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        project = self.projects[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:
                return project['name']
            elif col == 1:
                return project['role_name']
            elif col == 2:
                start = project['project_start'] or ""
                end = project['project_end'] or "継続中"
                if start:
                    start = start[:7]
                    if end != "継続中":
                        end = end[:7]
                    return f"{start} ~ {end}"
                return ""
            elif col == 3:
                return project['scale_text'] or ""
        
        elif role == Qt.UserRole:
            return project['id']
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def update_projects(self, projects):
        self.beginResetModel()
        # SQLAlchemyオブジェクトを辞書に変換してセッション依存を回避
        self.projects = []
        for project in projects:
            self.projects.append({
                'id': project.id,
                'name': project.name,
                'role_name': project.role.name if project.role else "",
                'project_start': project.project_start,
                'project_end': project.project_end,
                'scale_text': project.scale_text
            })
        self.endResetModel()

class TechUsageDialog(QDialog):
    def __init__(self, project_id, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.setWindowTitle("技術使用期間編集")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["種別", "技術名", "開始日", "終了日"])
        
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_view)
        
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("追加")
        self.add_button.clicked.connect(self.add_usage)
        button_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("削除")
        self.delete_button.clicked.connect(self.delete_usage)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        
        self.auto_button = QPushButton("プロジェクト期間で自動生成")
        self.auto_button.clicked.connect(self.auto_generate)
        button_layout.addWidget(self.auto_button)
        
        layout.addLayout(button_layout)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.save_and_close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.load_usages()
    
    def load_usages(self):
        self.table_model.setRowCount(0)
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            usages = repo.get_tech_usages_by_project(self.project_id)
            
            for usage in usages:
                kind_item = QStandardItem(usage.kind)
                kind_item.setData(usage.id, Qt.UserRole)
                
                master = repo.get_master_by_kind(usage.kind)
                tech_name = ""
                for m in master:
                    if m.id == usage.tech_id:
                        tech_name = m.name
                        break
                
                tech_item = QStandardItem(tech_name)
                tech_item.setData(usage.tech_id, Qt.UserRole)
                
                start_item = QStandardItem(usage.start or "")
                end_item = QStandardItem(usage.end or "")
                
                self.table_model.appendRow([kind_item, tech_item, start_item, end_item])
    
    def add_usage(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("技術使用期間追加")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        kind_combo = QComboBox()
        kind_combo.addItems(['os', 'language', 'framework', 'tool', 'cloud', 'db'])
        layout.addRow("種別:", kind_combo)
        
        tech_combo = QComboBox()
        layout.addRow("技術:", tech_combo)
        
        def update_tech_combo():
            tech_combo.clear()
            with db_service.session_scope() as session:
                repo = Repository(session)
                techs = repo.get_master_by_kind(kind_combo.currentText())
                for tech in techs:
                    tech_combo.addItem(tech.name, tech.id)
        
        kind_combo.currentTextChanged.connect(update_tech_combo)
        update_tech_combo()
        
        start_edit = QDateEdit()
        start_edit.setCalendarPopup(True)
        start_edit.setDate(QDate.currentDate())
        start_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addRow("開始日:", start_edit)
        
        end_edit = QDateEdit()
        end_edit.setCalendarPopup(True)
        end_edit.setDate(QDate.currentDate())
        end_edit.setDisplayFormat("yyyy-MM-dd")
        end_edit.setSpecialValueText("継続中")
        layout.addRow("終了日:", end_edit)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            kind_item = QStandardItem(kind_combo.currentText())
            kind_item.setData(0, Qt.UserRole)
            
            tech_item = QStandardItem(tech_combo.currentText())
            tech_item.setData(tech_combo.currentData(), Qt.UserRole)
            
            start_item = QStandardItem(start_edit.date().toString("yyyy-MM-dd"))
            
            end_text = ""
            if end_edit.date() != end_edit.minimumDate():
                end_text = end_edit.date().toString("yyyy-MM-dd")
            end_item = QStandardItem(end_text)
            
            self.table_model.appendRow([kind_item, tech_item, start_item, end_item])
    
    def delete_usage(self):
        current = self.table_view.currentIndex()
        if current.isValid():
            self.table_model.removeRow(current.row())
    
    def auto_generate(self):
        reply = QMessageBox.question(
            self, "確認",
            "既存の技術使用期間をクリアして、プロジェクト期間で自動生成しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            with db_service.session_scope() as session:
                repo = Repository(session)
                repo.auto_generate_tech_usages_from_project(self.project_id)
            
            self.load_usages()
            QMessageBox.information(self, "完了", "技術使用期間を自動生成しました")
    
    def save_and_close(self):
        try:
            with db_service.session_scope() as session:
                repo = Repository(session)
                
                existing = repo.get_tech_usages_by_project(self.project_id)
                for usage in existing:
                    repo.delete_tech_usage(usage.id)
                
                for row in range(self.table_model.rowCount()):
                    kind_item = self.table_model.item(row, 0)
                    tech_item = self.table_model.item(row, 1)
                    start_item = self.table_model.item(row, 2)
                    end_item = self.table_model.item(row, 3)
                    
                    data = {
                        'project_id': self.project_id,
                        'kind': kind_item.text(),
                        'tech_id': tech_item.data(Qt.UserRole),
                        'start': start_item.text() if start_item.text() else None,
                        'end': end_item.text() if end_item.text() else None
                    }
                    repo.create_tech_usage(data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"保存に失敗しました: {str(e)}")

class ProjectsView(QWidget):
    data_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_project_id = None
        self.init_ui()
        self.load_masters()
        self.refresh_data()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        filter_group = QGroupBox("フィルタ")
        filter_layout = QVBoxLayout()
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("期間:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setSpecialValueText("指定なし")
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("〜"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setSpecialValueText("指定なし")
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.end_date)
        filter_layout.addLayout(date_layout)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("検索:"))
        self.search_text = QLineEdit()
        self.search_text.setPlaceholderText("プロジェクト名/業務内容で検索")
        search_layout.addWidget(self.search_text)
        
        self.search_button = QPushButton("検索")
        self.search_button.clicked.connect(self.refresh_data)
        search_layout.addWidget(self.search_button)
        filter_layout.addLayout(search_layout)
        
        filter_group.setLayout(filter_layout)
        left_layout.addWidget(filter_group)
        
        self.project_table = QTableView()
        self.project_model = ProjectTableModel()
        self.project_table.setModel(self.project_model)
        self.project_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.project_table.selectionModel().selectionChanged.connect(self.on_project_selected)
        left_layout.addWidget(self.project_table)
        
        button_layout = QHBoxLayout()
        self.new_button = QPushButton("新規")
        self.new_button.clicked.connect(self.new_project)
        button_layout.addWidget(self.new_button)
        
        self.duplicate_button = QPushButton("複製")
        self.duplicate_button.clicked.connect(self.duplicate_project)
        button_layout.addWidget(self.duplicate_button)
        
        self.delete_button = QPushButton("削除")
        self.delete_button.clicked.connect(self.delete_project)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        left_layout.addLayout(button_layout)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.tab_widget = QTabWidget()
        right_layout.addWidget(self.tab_widget)
        
        self.overview_tab = QWidget()
        self.init_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "概要")
        
        self.engagement_tab = QWidget()
        self.init_engagement_tab()
        self.tab_widget.addTab(self.engagement_tab, "現場")
        
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        self.usage_button = QPushButton("技術使用期間編集")
        self.usage_button.clicked.connect(self.edit_tech_usage)
        save_layout.addWidget(self.usage_button)
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_project)
        save_layout.addWidget(self.save_button)
        
        right_layout.addLayout(save_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])
    
    def init_overview_tab(self):
        layout = QVBoxLayout(self.overview_tab)
        
        form_layout = QHBoxLayout()
        left_form = QVBoxLayout()
        right_form = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("プロジェクト名:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        left_form.addLayout(name_layout)
        
        summary_layout = QVBoxLayout()
        summary_layout.addWidget(QLabel("業務内容:"))
        self.summary_edit = QTextEdit()
        self.summary_edit.setMaximumHeight(80)
        summary_layout.addWidget(self.summary_edit)
        left_form.addLayout(summary_layout)
        
        detail_layout = QVBoxLayout()
        detail_layout.addWidget(QLabel("詳細:"))
        self.detail_edit = QTextEdit()
        self.detail_edit.setMaximumHeight(100)
        detail_layout.addWidget(self.detail_edit)
        left_form.addLayout(detail_layout)
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("期間:"))
        self.project_start = QDateEdit()
        self.project_start.setCalendarPopup(True)
        self.project_start.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.project_start)
        
        date_layout.addWidget(QLabel("〜"))
        self.project_end = QDateEdit()
        self.project_end.setCalendarPopup(True)
        self.project_end.setSpecialValueText("継続中")
        self.project_end.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.project_end)
        left_form.addLayout(date_layout)
        
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("役割:"))
        self.role_combo = QComboBox()
        role_layout.addWidget(self.role_combo)
        
        role_layout.addWidget(QLabel("作業:"))
        self.task_combo = QComboBox()
        role_layout.addWidget(self.task_combo)
        left_form.addLayout(role_layout)
        
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("規模:"))
        self.scale_edit = QLineEdit()
        self.scale_edit.setPlaceholderText("例: 要員約12名")
        scale_layout.addWidget(self.scale_edit)
        left_form.addLayout(scale_layout)
        
        tech_group = QGroupBox("使用技術")
        tech_layout = QVBoxLayout()
        
        tech_categories = [
            ('OS', 'os_list'),
            ('言語', 'language_list'),
            ('フレームワーク', 'framework_list'),
            ('ツール', 'tool_list'),
            ('クラウド', 'cloud_list'),
            ('データベース', 'db_list')
        ]
        
        for label, attr in tech_categories:
            cat_layout = QVBoxLayout()
            cat_layout.addWidget(QLabel(f"{label}:"))
            list_widget = QListWidget()
            list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
            list_widget.setMaximumHeight(80)
            setattr(self, attr, list_widget)
            cat_layout.addWidget(list_widget)
            tech_layout.addLayout(cat_layout)
        
        tech_group.setLayout(tech_layout)
        right_form.addWidget(tech_group)
        
        form_layout.addLayout(left_form, 1)
        form_layout.addLayout(right_form, 1)
        layout.addLayout(form_layout)
    
    def init_engagement_tab(self):
        layout = QVBoxLayout(self.engagement_tab)
        
        self.engagement_model = QStandardItemModel()
        self.engagement_model.setHorizontalHeaderLabels([
            "開始日", "終了日", "役割", "作業", "規模"
        ])
        
        self.engagement_table = QTableView()
        self.engagement_table.setModel(self.engagement_model)
        layout.addWidget(self.engagement_table)
        
        button_layout = QHBoxLayout()
        
        self.add_engagement_button = QPushButton("現場追加")
        self.add_engagement_button.clicked.connect(self.add_engagement)
        button_layout.addWidget(self.add_engagement_button)
        
        self.delete_engagement_button = QPushButton("現場削除")
        self.delete_engagement_button.clicked.connect(self.delete_engagement)
        button_layout.addWidget(self.delete_engagement_button)
        
        button_layout.addStretch()
        
        self.auto_engagement_button = QPushButton("選択現場で技術期間を自動生成")
        self.auto_engagement_button.clicked.connect(self.auto_generate_from_engagement)
        button_layout.addWidget(self.auto_engagement_button)
        
        layout.addLayout(button_layout)
    
    def load_masters(self):
        with db_service.session_scope() as session:
            repo = Repository(session)
            
            self.role_combo.clear()
            self.role_combo.addItem("", None)
            for role in repo.get_master_by_kind('role'):
                self.role_combo.addItem(role.name, role.id)
            
            self.task_combo.clear()
            self.task_combo.addItem("", None)
            for task in repo.get_master_by_kind('task'):
                self.task_combo.addItem(task.name, task.id)
            
            tech_lists = [
                ('os', self.os_list),
                ('language', self.language_list),
                ('framework', self.framework_list),
                ('tool', self.tool_list),
                ('cloud', self.cloud_list),
                ('db', self.db_list)
            ]
            
            for kind, list_widget in tech_lists:
                list_widget.clear()
                for tech in repo.get_master_by_kind(kind):
                    item = QListWidgetItem(tech.name)
                    item.setData(Qt.UserRole, tech.id)
                    list_widget.addItem(item)
    
    def refresh_data(self):
        filters = {}
        
        if self.start_date.date() != self.start_date.minimumDate():
            filters['start_date'] = self.start_date.date().toString("yyyy-MM-dd")
        
        if self.end_date.date() != self.end_date.minimumDate():
            filters['end_date'] = self.end_date.date().toString("yyyy-MM-dd")
        
        if self.search_text.text():
            filters['text'] = self.search_text.text()
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            projects = repo.filter_projects(filters)
            self.project_model.update_projects(projects)
    
    def on_project_selected(self, selected, deselected):
        indexes = self.project_table.selectionModel().selectedRows()
        if indexes:
            project_id = self.project_model.data(indexes[0], Qt.UserRole)
            self.load_project(project_id)
    
    def load_project(self, project_id):
        self.current_project_id = project_id
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            project = repo.get_project_by_id(project_id)
            
            if project:
                self.name_edit.setText(project.name or "")
                self.summary_edit.setText(project.work_summary or "")
                self.detail_edit.setText(project.detail or "")
                
                if project.project_start:
                    self.project_start.setDate(QDate.fromString(project.project_start, "yyyy-MM-dd"))
                else:
                    self.project_start.setDate(self.project_start.minimumDate())
                
                if project.project_end:
                    self.project_end.setDate(QDate.fromString(project.project_end, "yyyy-MM-dd"))
                else:
                    self.project_end.setDate(self.project_end.minimumDate())
                
                index = self.role_combo.findData(project.role_id)
                self.role_combo.setCurrentIndex(index if index >= 0 else 0)
                
                index = self.task_combo.findData(project.task_id)
                self.task_combo.setCurrentIndex(index if index >= 0 else 0)
                
                self.scale_edit.setText(project.scale_text or "")
                
                tech_lists = [
                    ('os', self.os_list),
                    ('language', self.language_list),
                    ('framework', self.framework_list),
                    ('tool', self.tool_list),
                    ('cloud', self.cloud_list),
                    ('db', self.db_list)
                ]
                
                for kind, list_widget in tech_lists:
                    list_widget.clearSelection()
                    selected_ids = repo.get_project_techs(project_id, kind)
                    
                    for i in range(list_widget.count()):
                        item = list_widget.item(i)
                        if item.data(Qt.UserRole) in selected_ids:
                            item.setSelected(True)
                
                self.load_engagements(project_id)
    
    def load_engagements(self, project_id):
        self.engagement_model.setRowCount(0)
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            engagements = repo.get_engagements_by_project(project_id)
            
            for eng in engagements:
                start_item = QStandardItem(eng.site_start or "")
                start_item.setData(eng.id, Qt.UserRole)
                
                end_item = QStandardItem(eng.site_end or "")
                
                role_name = ""
                if eng.role_override:
                    role_name = eng.role_override.name
                role_item = QStandardItem(role_name)
                role_item.setData(eng.role_override_id, Qt.UserRole)
                
                task_name = ""
                if eng.task_override:
                    task_name = eng.task_override.name
                task_item = QStandardItem(task_name)
                task_item.setData(eng.task_override_id, Qt.UserRole)
                
                scale_item = QStandardItem(eng.scale_override_text or "")
                
                self.engagement_model.appendRow([
                    start_item, end_item, role_item, task_item, scale_item
                ])
    
    def new_project(self):
        self.current_project_id = None
        self.name_edit.clear()
        self.summary_edit.clear()
        self.detail_edit.clear()
        self.project_start.setDate(QDate.currentDate())
        self.project_end.setDate(self.project_end.minimumDate())
        self.role_combo.setCurrentIndex(0)
        self.task_combo.setCurrentIndex(0)
        self.scale_edit.clear()
        
        for list_widget in [self.os_list, self.language_list, self.framework_list,
                           self.tool_list, self.cloud_list, self.db_list]:
            list_widget.clearSelection()
        
        self.engagement_model.setRowCount(0)
    
    def save_project(self):
        try:
            data = {
                'name': self.name_edit.text(),
                'work_summary': self.summary_edit.toPlainText(),
                'detail': self.detail_edit.toPlainText(),
                'project_start': self.project_start.date().toString("yyyy-MM-dd") if self.project_start.date() != self.project_start.minimumDate() else None,
                'project_end': self.project_end.date().toString("yyyy-MM-dd") if self.project_end.date() != self.project_end.minimumDate() else None,
                'role_id': self.role_combo.currentData(),
                'task_id': self.task_combo.currentData(),
                'scale_text': self.scale_edit.text()
            }
            
            with db_service.session_scope() as session:
                repo = Repository(session)
                
                if self.current_project_id:
                    project = repo.update_project(self.current_project_id, data)
                else:
                    project = repo.create_project(data)
                    self.current_project_id = project.id
                
                tech_lists = [
                    ('os', self.os_list),
                    ('language', self.language_list),
                    ('framework', self.framework_list),
                    ('tool', self.tool_list),
                    ('cloud', self.cloud_list),
                    ('db', self.db_list)
                ]
                
                for kind, list_widget in tech_lists:
                    selected_ids = []
                    for i in range(list_widget.count()):
                        item = list_widget.item(i)
                        if item.isSelected():
                            selected_ids.append(item.data(Qt.UserRole))
                    repo.link_project_tech(self.current_project_id, kind, selected_ids)
                
                for row in range(self.engagement_model.rowCount()):
                    eng_id = self.engagement_model.item(row, 0).data(Qt.UserRole)
                    eng_data = {
                        'project_id': self.current_project_id,
                        'site_start': self.engagement_model.item(row, 0).text(),
                        'site_end': self.engagement_model.item(row, 1).text() or None,
                        'role_override_id': self.engagement_model.item(row, 2).data(Qt.UserRole),
                        'task_override_id': self.engagement_model.item(row, 3).data(Qt.UserRole),
                        'scale_override_text': self.engagement_model.item(row, 4).text() or None
                    }
                    
                    if eng_id and eng_id > 0:
                        repo.update_engagement(eng_id, eng_data)
                    else:
                        repo.create_engagement(eng_data)
            
            self.refresh_data()
            self.data_changed.emit()
            QMessageBox.information(self, "成功", "プロジェクトを保存しました")
            
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"保存に失敗しました: {str(e)}")
    
    def delete_project(self):
        if not self.current_project_id:
            return
        
        reply = QMessageBox.question(
            self, "確認",
            "選択したプロジェクトを削除しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.delete_project(self.current_project_id)
                
                self.new_project()
                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "プロジェクトを削除しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"削除に失敗しました: {str(e)}")
    
    def duplicate_project(self):
        if not self.current_project_id:
            return
        
        self.save_project()
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            original = repo.get_project_by_id(self.current_project_id)
            
            if original:
                data = {
                    'name': f"{original.name} (コピー)",
                    'work_summary': original.work_summary,
                    'detail': original.detail,
                    'project_start': original.project_start,
                    'project_end': original.project_end,
                    'role_id': original.role_id,
                    'task_id': original.task_id,
                    'scale_text': original.scale_text
                }
                
                new_project = repo.create_project(data)
                
                for kind in ['os', 'language', 'framework', 'tool', 'cloud', 'db']:
                    tech_ids = repo.get_project_techs(self.current_project_id, kind)
                    repo.link_project_tech(new_project.id, kind, tech_ids)
        
        self.refresh_data()
        self.data_changed.emit()
        QMessageBox.information(self, "成功", "プロジェクトを複製しました")
    
    def add_engagement(self):
        new_row = []
        new_row.append(QStandardItem(QDate.currentDate().toString("yyyy-MM-dd")))
        new_row[0].setData(0, Qt.UserRole)
        new_row.append(QStandardItem(""))
        new_row.append(QStandardItem(""))
        new_row.append(QStandardItem(""))
        new_row.append(QStandardItem(""))
        
        self.engagement_model.appendRow(new_row)
    
    def delete_engagement(self):
        current = self.engagement_table.currentIndex()
        if current.isValid():
            eng_id = self.engagement_model.item(current.row(), 0).data(Qt.UserRole)
            if eng_id and eng_id > 0:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.delete_engagement(eng_id)
            
            self.engagement_model.removeRow(current.row())
    
    def edit_tech_usage(self):
        if not self.current_project_id:
            QMessageBox.warning(self, "警告", "プロジェクトを選択してください")
            return
        
        dialog = TechUsageDialog(self.current_project_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.data_changed.emit()
    
    def auto_generate_from_engagement(self):
        current = self.engagement_table.currentIndex()
        if not current.isValid():
            QMessageBox.warning(self, "警告", "現場を選択してください")
            return
        
        if not self.current_project_id:
            QMessageBox.warning(self, "警告", "プロジェクトを保存してから実行してください")
            return
        
        eng_id = self.engagement_model.item(current.row(), 0).data(Qt.UserRole)
        if not eng_id or eng_id <= 0:
            QMessageBox.warning(self, "警告", "現場を保存してから実行してください")
            return
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            repo.auto_generate_tech_usages_from_engagement(self.current_project_id, eng_id)
        
        QMessageBox.information(self, "完了", "選択した現場期間で技術使用期間を生成しました")