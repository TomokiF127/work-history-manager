from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTableView, QPushButton, QLineEdit, QComboBox,
    QLabel, QGroupBox, QDateEdit, QMessageBox,
    QTabWidget, QTextEdit, QListWidget, QListWidgetItem,
    QAbstractItemView, QHeaderView, QDialog, QDialogButtonBox,
    QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt, QDate, Signal, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem, QKeySequence, QShortcut
from ui.styles import BUTTON_STYLES
from datetime import date, datetime
from typing import List, Optional
from services.db import db_service
from services.repository import Repository

class ProjectTableModel(QAbstractTableModel):
    def __init__(self, projects=None):
        super().__init__()
        self.projects = []
        self.headers = ["プロジェクト名", "役割", "期間", "規模", "エンドユーザー", "契約会社"]
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
            elif col == 4:
                return project['end_user'] or ""
            elif col == 5:
                return project['contract_company'] or ""
        
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
                'scale_text': project.scale_text,
                'end_user': project.end_user,
                'contract_company': project.contract_company
            })
        self.endResetModel()

class RoleSelectionDialog(QDialog):
    def __init__(self, selected_role_ids, parent=None):
        super().__init__(parent)
        self.selected_role_ids = selected_role_ids.copy() if selected_role_ids else []
        self.all_roles = []  # 全ての役割データを保持
        self.setWindowTitle("役割選択")
        self.setModal(True)
        self.resize(400, 500)

        layout = QVBoxLayout(self)

        # 説明ラベル
        info_label = QLabel("役割を複数選択できます:")
        layout.addWidget(info_label)

        # 検索ボックス
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("検索:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("役割名で検索...")
        self.search_box.textChanged.connect(self.filter_roles)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # リストウィジェット
        self.role_list = QListWidget()
        self.role_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.role_list)

        # マスターデータを読み込み
        self.load_roles()

        # ボタン
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_roles(self):
        with db_service.session_scope() as session:
            repo = Repository(session)
            roles = repo.get_master_by_kind('role')

            # 全ての役割データを保持
            self.all_roles = [(role.id, role.name) for role in roles]

            # リストに表示
            self.filter_roles()

    def filter_roles(self):
        """検索テキストに基づいて役割をフィルタリング"""
        search_text = self.search_box.text().lower() if hasattr(self, 'search_box') else ""

        # 現在の選択状態を保存
        current_selections = {self.role_list.item(i).data(Qt.UserRole)
                             for i in range(self.role_list.count())
                             if self.role_list.item(i).isSelected()}

        # リストをクリア
        self.role_list.clear()

        # フィルタリングして表示
        for role_id, role_name in self.all_roles:
            if search_text in role_name.lower():
                item = QListWidgetItem(role_name)
                item.setData(Qt.UserRole, role_id)
                self.role_list.addItem(item)

                # 選択状態を復元
                if role_id in self.selected_role_ids or role_id in current_selections:
                    item.setSelected(True)

    def get_selected_ids(self):
        """選択された役割IDのリストを返す"""
        selected = []
        for i in range(self.role_list.count()):
            item = self.role_list.item(i)
            if item.isSelected():
                selected.append(item.data(Qt.UserRole))
        return selected

    def get_selected_names(self):
        """選択された役割名のリストを返す"""
        selected = []
        for i in range(self.role_list.count()):
            item = self.role_list.item(i)
            if item.isSelected():
                selected.append(item.text())
        return selected

class TaskSelectionDialog(QDialog):
    def __init__(self, selected_task_ids, parent=None):
        super().__init__(parent)
        self.selected_task_ids = selected_task_ids.copy() if selected_task_ids else []
        self.all_tasks = []  # 全ての作業データを保持
        self.setWindowTitle("作業選択")
        self.setModal(True)
        self.resize(400, 500)

        layout = QVBoxLayout(self)

        # 説明ラベル
        info_label = QLabel("作業を複数選択できます:")
        layout.addWidget(info_label)

        # 検索ボックス
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("検索:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("作業名で検索...")
        self.search_box.textChanged.connect(self.filter_tasks)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # リストウィジェット
        self.task_list = QListWidget()
        self.task_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.task_list)

        # マスターデータを読み込み
        self.load_tasks()

        # ボタン
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_tasks(self):
        with db_service.session_scope() as session:
            repo = Repository(session)
            tasks = repo.get_master_by_kind('task')

            # 全ての作業データを保持
            self.all_tasks = [(task.id, task.name) for task in tasks]

            # リストに表示
            self.filter_tasks()

    def filter_tasks(self):
        """検索テキストに基づいて作業をフィルタリング"""
        search_text = self.search_box.text().lower() if hasattr(self, 'search_box') else ""

        # 現在の選択状態を保存
        current_selections = {self.task_list.item(i).data(Qt.UserRole)
                             for i in range(self.task_list.count())
                             if self.task_list.item(i).isSelected()}

        # リストをクリア
        self.task_list.clear()

        # フィルタリングして表示
        for task_id, task_name in self.all_tasks:
            if search_text in task_name.lower():
                item = QListWidgetItem(task_name)
                item.setData(Qt.UserRole, task_id)
                self.task_list.addItem(item)

                # 選択状態を復元
                if task_id in self.selected_task_ids or task_id in current_selections:
                    item.setSelected(True)

    def get_selected_ids(self):
        """選択された作業IDのリストを返す"""
        selected = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item.isSelected():
                selected.append(item.data(Qt.UserRole))
        return selected

    def get_selected_names(self):
        """選択された作業名のリストを返す"""
        selected = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item.isSelected():
                selected.append(item.text())
        return selected

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
        start_edit.setDisplayFormat("yyyy年MM月dd日")
        layout.addRow("開始日:", start_edit)
        
        end_edit = QDateEdit()
        end_edit.setCalendarPopup(True)
        end_edit.setDate(QDate.currentDate())
        end_edit.setDisplayFormat("yyyy年MM月dd日")
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
        self.set_default_filters()
        self.refresh_data()
        self.setup_shortcuts()
    
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
        self.start_date.setDisplayFormat("yyyy年MM月dd日")
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("〜"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setSpecialValueText("指定なし")
        self.end_date.setDisplayFormat("yyyy年MM月dd日")
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
        
        # 横スクロールを有効化し、カラムサイズを調整
        self.project_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.project_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.project_table.horizontalHeader().setStretchLastSection(False)
        self.project_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # 各カラムの初期幅を設定
        header = self.project_table.horizontalHeader()
        header.resizeSection(0, 200)  # プロジェクト名
        header.resizeSection(1, 100)  # 役割
        header.resizeSection(2, 180)  # 期間
        header.resizeSection(3, 150)  # 規模
        
        left_layout.addWidget(self.project_table)
        
        button_layout = QHBoxLayout()
        self.new_button = QPushButton("新規")
        self.new_button.setStyleSheet(BUTTON_STYLES['success'])
        self.new_button.clicked.connect(self.new_project)
        button_layout.addWidget(self.new_button)
        
        self.duplicate_button = QPushButton("複製")
        self.duplicate_button.setStyleSheet(BUTTON_STYLES['secondary'])
        self.duplicate_button.clicked.connect(self.duplicate_project)
        button_layout.addWidget(self.duplicate_button)
        
        self.delete_button = QPushButton("削除")
        self.delete_button.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_button.clicked.connect(self.delete_project)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        left_layout.addLayout(button_layout)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.tab_widget = QTabWidget()
        right_layout.addWidget(self.tab_widget)
        
        self.basic_info_tab = QWidget()
        self.init_basic_info_tab()
        self.tab_widget.addTab(self.basic_info_tab, "基本情報")
        
        self.tech_tab = QWidget()
        self.init_tech_tab()
        self.tab_widget.addTab(self.tech_tab, "使用技術")
        
        
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        self.usage_button = QPushButton("技術使用期間編集")
        self.usage_button.clicked.connect(self.edit_tech_usage)
        save_layout.addWidget(self.usage_button)
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_project)
        save_layout.addWidget(self.save_button)
        
        self.sync_all_button = QPushButton("全プロジェクト技術同期")
        self.sync_all_button.clicked.connect(self.sync_all_projects)
        save_layout.addWidget(self.sync_all_button)
        
        right_layout.addLayout(save_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])
    
    def init_basic_info_tab(self):
        layout = QVBoxLayout(self.basic_info_tab)
        
        # 上部: プロジェクト概要情報
        overview_group = QGroupBox("プロジェクト概要")
        overview_layout = QVBoxLayout()
        
        # プロジェクト名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("プロジェクト名:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        overview_layout.addLayout(name_layout)
        
        # 第1行: 期間と規模
        first_row_layout = QHBoxLayout()
        
        # 期間
        first_row_layout.addWidget(QLabel("期間:"))
        self.project_start = QDateEdit()
        self.project_start.setCalendarPopup(True)
        self.project_start.setDisplayFormat("yyyy年MM月dd日")
        first_row_layout.addWidget(self.project_start)
        
        first_row_layout.addWidget(QLabel("〜"))
        self.project_end = QDateEdit()
        self.project_end.setCalendarPopup(True)
        self.project_end.setSpecialValueText("継続中")
        self.project_end.setDisplayFormat("yyyy年MM月dd日")
        first_row_layout.addWidget(self.project_end)
        
        first_row_layout.addStretch()
        
        # 規模
        first_row_layout.addWidget(QLabel("規模:"))
        self.scale_edit = QLineEdit()
        self.scale_edit.setPlaceholderText("例: 要員約12名")
        self.scale_edit.setMinimumWidth(150)
        first_row_layout.addWidget(self.scale_edit)
        
        overview_layout.addLayout(first_row_layout)
        
        # 第2行: 役割と作業
        second_row_layout = QHBoxLayout()

        # 役割
        role_layout = QVBoxLayout()
        role_layout.addWidget(QLabel("役割:"))
        self.role_button = QPushButton("選択...")
        self.role_button.clicked.connect(self.open_role_dialog)
        self.role_button.setMinimumWidth(120)
        role_layout.addWidget(self.role_button)
        self.selected_roles = []  # 選択された役割IDリスト
        second_row_layout.addLayout(role_layout)

        # 作業
        task_layout = QVBoxLayout()
        task_layout.addWidget(QLabel("作業:"))
        self.task_button = QPushButton("選択...")
        self.task_button.clicked.connect(self.open_task_dialog)
        self.task_button.setMinimumWidth(120)
        task_layout.addWidget(self.task_button)
        self.selected_tasks = []  # 選択された作業IDリスト
        second_row_layout.addLayout(task_layout)

        overview_layout.addLayout(second_row_layout)
        
        # 第3行: エンドユーザーと契約会社（幅広く）
        business_layout = QHBoxLayout()
        business_layout.addWidget(QLabel("エンドユーザー:"))
        self.end_user_edit = QLineEdit()
        self.end_user_edit.setMinimumWidth(200)
        business_layout.addWidget(self.end_user_edit)
        
        business_layout.addWidget(QLabel("契約会社:"))
        self.contract_company_edit = QLineEdit()
        self.contract_company_edit.setMinimumWidth(200)
        business_layout.addWidget(self.contract_company_edit)
        
        overview_layout.addLayout(business_layout)
        
        # 業務内容
        summary_layout = QVBoxLayout()
        summary_layout.addWidget(QLabel("業務内容:"))
        self.summary_edit = QTextEdit()
        self.summary_edit.setMinimumHeight(100)
        self.summary_edit.setMaximumHeight(150)
        summary_layout.addWidget(self.summary_edit)
        overview_layout.addLayout(summary_layout)
        
        # 詳細
        detail_layout = QVBoxLayout()
        detail_layout.addWidget(QLabel("詳細:"))
        self.detail_edit = QTextEdit()
        self.detail_edit.setMinimumHeight(120)
        self.detail_edit.setMaximumHeight(200)
        detail_layout.addWidget(self.detail_edit)
        overview_layout.addLayout(detail_layout)
        
        # 備考
        remarks_layout = QVBoxLayout()
        remarks_layout.addWidget(QLabel("備考:"))
        self.remarks_edit = QTextEdit()
        self.remarks_edit.setMinimumHeight(80)
        self.remarks_edit.setMaximumHeight(200)
        remarks_layout.addWidget(self.remarks_edit)
        overview_layout.addLayout(remarks_layout)
        
        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)
        layout.addStretch()
    
    def init_tech_tab(self):
        layout = QVBoxLayout(self.tech_tab)
        
        # 使用技術
        tech_group = QGroupBox("使用技術")
        tech_main_layout = QVBoxLayout()
        
        # 技術を2行3列で配置
        tech_grid_layout1 = QHBoxLayout()
        tech_grid_layout2 = QHBoxLayout()
        
        tech_categories = [
            ('OS', 'os_list'),
            ('言語', 'language_list'),
            ('FW/ライブラリ', 'framework_list'),
            ('ツール', 'tool_list'),
            ('クラウド', 'cloud_list'),
            ('データベース', 'db_list')
        ]
        
        for i, (label, attr) in enumerate(tech_categories):
            cat_widget = QWidget()
            cat_layout = QVBoxLayout(cat_widget)
            cat_layout.setContentsMargins(5, 5, 5, 5)
            
            cat_layout.addWidget(QLabel(f"{label}:"))
            list_widget = QListWidget()
            list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
            list_widget.setMaximumHeight(150)
            setattr(self, attr, list_widget)
            cat_layout.addWidget(list_widget)
            
            if i < 3:
                tech_grid_layout1.addWidget(cat_widget)
            else:
                tech_grid_layout2.addWidget(cat_widget)
        
        tech_main_layout.addLayout(tech_grid_layout1)
        tech_main_layout.addLayout(tech_grid_layout2)
        
        tech_group.setLayout(tech_main_layout)
        layout.addWidget(tech_group)
        layout.addStretch()
    
    
    def sync_tech_usages_with_project_selections(self, repo, project_id):
        """プロジェクトの技術選択とtech_usagesを同期"""
        try:
            project = repo.get_project_by_id(project_id)
            if not project:
                return
            
            # 現在のtech_usagesを削除
            repo.delete_tech_usages_by_project(project_id)
            
            # プロジェクトの技術選択から新しいtech_usagesを生成
            tech_kinds = ['os', 'language', 'framework', 'tool', 'cloud', 'db']
            
            for kind in tech_kinds:
                selected_tech_ids = repo.get_project_techs(project_id, kind)
                
                for tech_id in selected_tech_ids:
                    # プロジェクト期間をデフォルトの技術使用期間として設定
                    repo.create_tech_usage({
                        'project_id': project_id,
                        'kind': kind,
                        'tech_id': tech_id,
                        'start': project.project_start,
                        'end': project.project_end
                    })
                    
        except Exception as e:
            print(f"技術使用期間同期エラー: {e}")
    
    def open_role_dialog(self):
        """役割選択ダイアログを開く"""
        dialog = RoleSelectionDialog(self.selected_roles, self)
        if dialog.exec_() == QDialog.Accepted:
            self.selected_roles = dialog.get_selected_ids()
            # ボタンのテキストを更新
            names = dialog.get_selected_names()
            if names:
                self.role_button.setText(", ".join(names))
            else:
                self.role_button.setText("選択...")

    def open_task_dialog(self):
        """作業選択ダイアログを開く"""
        dialog = TaskSelectionDialog(self.selected_tasks, self)
        if dialog.exec_() == QDialog.Accepted:
            self.selected_tasks = dialog.get_selected_ids()
            # ボタンのテキストを更新
            names = dialog.get_selected_names()
            if names:
                self.task_button.setText(", ".join(names))
            else:
                self.task_button.setText("選択...")

    def load_masters(self):
        with db_service.session_scope() as session:
            repo = Repository(session)

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
    
    def set_default_filters(self):
        """デフォルトのフィルタを設定（全期間）"""
        # 最も古いプロジェクトの開始日を取得
        try:
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
                    
                    # デフォルト値を設定
                    if oldest_date:
                        self.start_date.setDate(oldest_date)
                    else:
                        self.start_date.setDate(QDate.currentDate().addYears(-10))
                    
                    self.end_date.setDate(QDate.currentDate())
                else:
                    # プロジェクトがない場合のデフォルト
                    self.start_date.setDate(QDate.currentDate().addYears(-10))
                    self.end_date.setDate(QDate.currentDate())
        except Exception as e:
            print(f"フィルタ設定エラー: {e}")
            # エラー時のデフォルト
            self.start_date.setDate(QDate.currentDate().addYears(-10))
            self.end_date.setDate(QDate.currentDate())
    
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

                # 役割の複数選択を復元
                self.selected_roles = repo.get_project_roles(project_id)
                role_names = []
                for role in repo.get_master_by_kind('role'):
                    if role.id in self.selected_roles:
                        role_names.append(role.name)
                if role_names:
                    self.role_button.setText(", ".join(role_names))
                else:
                    self.role_button.setText("選択...")

                # 作業の複数選択を復元
                self.selected_tasks = repo.get_project_tasks(project_id)
                task_names = []
                for task in repo.get_master_by_kind('task'):
                    if task.id in self.selected_tasks:
                        task_names.append(task.name)
                if task_names:
                    self.task_button.setText(", ".join(task_names))
                else:
                    self.task_button.setText("選択...")

                self.scale_edit.setText(project.scale_text or "")
                self.end_user_edit.setText(project.end_user or "")
                self.contract_company_edit.setText(project.contract_company or "")
                self.remarks_edit.setText(project.remarks or "")
                
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
                
    
    def new_project(self):
        self.current_project_id = None
        self.name_edit.clear()
        self.summary_edit.clear()
        self.detail_edit.clear()
        self.project_start.setDate(QDate.currentDate())
        self.project_end.setDate(self.project_end.minimumDate())

        # 役割と作業の選択をクリア
        self.selected_roles = []
        self.selected_tasks = []
        self.role_button.setText("選択...")
        self.task_button.setText("選択...")

        self.scale_edit.clear()
        self.end_user_edit.clear()
        self.contract_company_edit.clear()
        self.remarks_edit.clear()

        for list_widget in [self.os_list, self.language_list, self.framework_list,
                           self.tool_list, self.cloud_list, self.db_list]:
            list_widget.clearSelection()
    
    def save_project(self):
        try:
            # バリデーション: プロジェクト名
            if not self.name_edit.text().strip():
                QMessageBox.warning(self, "警告", "プロジェクト名を入力してください")
                self.name_edit.setFocus()
                return

            # バリデーション: 日付の整合性チェック
            start_date = self.project_start.date()
            end_date = self.project_end.date()

            if start_date != self.project_start.minimumDate() and end_date != self.project_end.minimumDate():
                if start_date > end_date:
                    reply = QMessageBox.question(
                        self, "確認",
                        "開始日が終了日より後になっています。\nこのまま保存しますか？",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return

            is_new_project = False
            data = {
                'name': self.name_edit.text().strip(),
                'work_summary': self.summary_edit.toPlainText(),
                'detail': self.detail_edit.toPlainText(),
                'project_start': self.project_start.date().toString("yyyy-MM-dd") if self.project_start.date() != self.project_start.minimumDate() else None,
                'project_end': self.project_end.date().toString("yyyy-MM-dd") if self.project_end.date() != self.project_end.minimumDate() else None,
                'role_id': self.selected_roles[0] if self.selected_roles else None,
                'task_id': self.selected_tasks[0] if self.selected_tasks else None,
                'scale_text': self.scale_edit.text(),
                'end_user': self.end_user_edit.text(),
                'contract_company': self.contract_company_edit.text(),
                'remarks': self.remarks_edit.toPlainText()
            }

            with db_service.session_scope() as session:
                repo = Repository(session)

                if self.current_project_id:
                    project = repo.update_project(self.current_project_id, data)
                else:
                    project = repo.create_project(data)
                    self.current_project_id = project.id
                    is_new_project = True

                # 役割と作業の複数選択を保存
                repo.link_project_roles(self.current_project_id, self.selected_roles)
                repo.link_project_tasks(self.current_project_id, self.selected_tasks)

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

                # プロジェクト保存時に技術使用期間を同期
                self.sync_tech_usages_with_project_selections(repo, self.current_project_id)
                
            
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
                    'scale_text': original.scale_text,
                    'end_user': original.end_user,
                    'contract_company': original.contract_company,
                    'remarks': original.remarks
                }

                new_project = repo.create_project(data)

                # 役割と作業の複数選択を複製
                role_ids = repo.get_project_roles(self.current_project_id)
                repo.link_project_roles(new_project.id, role_ids)

                task_ids = repo.get_project_tasks(self.current_project_id)
                repo.link_project_tasks(new_project.id, task_ids)

                # 技術を複製
                for kind in ['os', 'language', 'framework', 'tool', 'cloud', 'db']:
                    tech_ids = repo.get_project_techs(self.current_project_id, kind)
                    repo.link_project_tech(new_project.id, kind, tech_ids)

        self.refresh_data()
        self.data_changed.emit()
        QMessageBox.information(self, "成功", "プロジェクトを複製しました")
    
    
    def edit_tech_usage(self):
        if not self.current_project_id:
            QMessageBox.warning(self, "警告", "プロジェクトを選択してください")
            return
        
        dialog = TechUsageDialog(self.current_project_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.data_changed.emit()
    
    def sync_all_projects(self):
        """全プロジェクトの技術選択とtech_usagesを同期"""
        reply = QMessageBox.question(
            self, "確認",
            "全プロジェクトの技術使用期間を選択されている技術と同期しますか？\n"
            "既存の技術使用期間データは上書きされます。",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    projects = repo.get_all_projects()

                    synced_count = 0
                    for project in projects:
                        self.sync_tech_usages_with_project_selections(repo, project.id)
                        synced_count += 1

                    self.refresh_data()
                    self.data_changed.emit()
                    QMessageBox.information(
                        self, "成功",
                        f"{synced_count}件のプロジェクトで技術使用期間を同期しました"
                    )
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"同期に失敗しました: {str(e)}")

    def setup_shortcuts(self):
        """キーボードショートカットを設定"""
        # Ctrl+S: 保存
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_project)

        # Ctrl+N: 新規
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.new_project)

        # Ctrl+D: 複製
        duplicate_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        duplicate_shortcut.activated.connect(self.duplicate_project)

        # Delete: 削除
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_project)

        # Ctrl+F: 検索フィールドにフォーカス
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_text.setFocus())
    
