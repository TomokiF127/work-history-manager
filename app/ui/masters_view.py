from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableView, QPushButton, QLineEdit, QTextEdit,
    QLabel, QMessageBox, QDialog, QDialogButtonBox,
    QFormLayout, QHeaderView, QComboBox
)
from PySide6.QtCore import Qt, Signal, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List
from services.db import db_service
from services.repository import Repository
from ui.styles import BUTTON_STYLES

class MasterTableModel(QAbstractTableModel):
    def __init__(self, kind, data=None):
        super().__init__()
        self.kind = kind
        self.data_list = []
        # 役割と作業と習熟度の場合は順序カラムを追加
        if kind in ['role', 'task', 'proficiency']:
            self.headers = ["順序", "名称", "備考"]
        else:
            self.headers = ["名称", "備考"]
        if data:
            self.update_data(data)

    def rowCount(self, parent=QModelIndex()):
        return len(self.data_list)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self.data_list[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if self.kind in ['role', 'task', 'proficiency']:
                if col == 0:
                    return str(item.get('order_index', 0))
                elif col == 1:
                    return item['name']
                elif col == 2:
                    return item['note'] or ""
            else:
                if col == 0:
                    return item['name']
                elif col == 1:
                    return item['note'] or ""
        elif role == Qt.UserRole:
            return item['id']

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

    def update_data(self, data):
        self.beginResetModel()
        # SQLAlchemyオブジェクトを辞書に変換してセッション依存を回避
        self.data_list = []
        for item in data:
            item_dict = {
                'id': item.id,
                'name': item.name,
                'note': item.note
            }
            # 役割と作業と習熟度の場合はorder_indexも保存
            if self.kind in ['role', 'task', 'proficiency'] and hasattr(item, 'order_index'):
                item_dict['order_index'] = item.order_index
            self.data_list.append(item_dict)
        self.endResetModel()

class MasterEditDialog(QDialog):
    def __init__(self, kind, master_id=None, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.master_id = master_id
        self.setWindowTitle("マスタ編集" if master_id else "マスタ追加")
        self.setModal(True)
        self.resize(400, 250)

        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        layout.addRow("名称:", self.name_edit)

        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(80)
        layout.addRow("備考:", self.note_edit)

        # 技術マスタの場合は習熟度選択を追加
        self.proficiency_combo = None
        if kind in ['os', 'language', 'framework', 'tool', 'cloud', 'db']:
            self.proficiency_combo = QComboBox()
            self.proficiency_combo.addItem("(未選択)", None)
            with db_service.session_scope() as session:
                repo = Repository(session)
                proficiencies = repo.get_master_by_kind('proficiency')
                for prof in proficiencies:
                    self.proficiency_combo.addItem(prof.name, prof.id)
            layout.addRow("習熟度:", self.proficiency_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if master_id:
            self.load_data()
    
    def load_data(self):
        with db_service.session_scope() as session:
            repo = Repository(session)
            masters = repo.get_master_by_kind(self.kind)
            for master in masters:
                if master.id == self.master_id:
                    self.name_edit.setText(master.name)
                    self.note_edit.setText(master.note or "")
                    # 習熟度が設定されている場合は選択状態にする
                    if self.proficiency_combo and hasattr(master, 'proficiency_id'):
                        if master.proficiency_id:
                            for i in range(self.proficiency_combo.count()):
                                if self.proficiency_combo.itemData(i) == master.proficiency_id:
                                    self.proficiency_combo.setCurrentIndex(i)
                                    break
                    break
    
    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "名称を入力してください")
            return
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            masters = repo.get_master_by_kind(self.kind)
            
            for master in masters:
                if master.name == self.name_edit.text().strip():
                    if not self.master_id or master.id != self.master_id:
                        QMessageBox.warning(self, "警告", "同じ名称が既に存在します")
                        return
        
        self.accept()
    
    def get_data(self):
        data = {
            'name': self.name_edit.text().strip(),
            'note': self.note_edit.toPlainText() or None
        }
        # 習熟度が選択されている場合は含める
        if self.proficiency_combo:
            proficiency_id = self.proficiency_combo.currentData()
            data['proficiency_id'] = proficiency_id
        return data

class MasterTabWidget(QWidget):
    data_changed = Signal()
    
    def __init__(self, kind, title):
        super().__init__()
        self.kind = kind
        self.title = title
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)

        self.table_view = QTableView()
        self.model = MasterTableModel(self.kind)
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_view)

        button_layout = QHBoxLayout()

        self.add_button = QPushButton("追加")
        self.add_button.setStyleSheet(BUTTON_STYLES['success'])
        self.add_button.clicked.connect(self.add_master)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("編集")
        self.edit_button.setStyleSheet(BUTTON_STYLES['primary'])
        self.edit_button.clicked.connect(self.edit_master)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("削除")
        self.delete_button.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_button.clicked.connect(self.delete_master)
        button_layout.addWidget(self.delete_button)

        # 役割と作業と習熟度の場合は並び替えボタンを追加
        if self.kind in ['role', 'task', 'proficiency']:
            button_layout.addStretch()

            self.move_up_button = QPushButton("↑ 上へ")
            self.move_up_button.setStyleSheet(BUTTON_STYLES['secondary'])
            self.move_up_button.clicked.connect(self.move_up)
            button_layout.addWidget(self.move_up_button)

            self.move_down_button = QPushButton("↓ 下へ")
            self.move_down_button.setStyleSheet(BUTTON_STYLES['secondary'])
            self.move_down_button.clicked.connect(self.move_down)
            button_layout.addWidget(self.move_down_button)
        else:
            button_layout.addStretch()

        layout.addLayout(button_layout)
    
    def refresh_data(self):
        with db_service.session_scope() as session:
            repo = Repository(session)
            data = repo.get_master_by_kind(self.kind)
            self.model.update_data(data)
    
    def add_master(self):
        dialog = MasterEditDialog(self.kind, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.create_master(
                        self.kind,
                        data['name'],
                        data['note'],
                        data.get('proficiency_id')
                    )

                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", f"{self.title}を追加しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"追加に失敗しました: {str(e)}")
    
    def edit_master(self):
        current = self.table_view.currentIndex()
        if not current.isValid():
            QMessageBox.warning(self, "警告", f"{self.title}を選択してください")
            return

        master_id = self.model.data(current.siblingAtColumn(0), Qt.UserRole)

        dialog = MasterEditDialog(self.kind, master_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.update_master(
                        self.kind,
                        master_id,
                        data['name'],
                        data['note'],
                        data.get('proficiency_id')
                    )

                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", f"{self.title}を更新しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"更新に失敗しました: {str(e)}")
    
    def delete_master(self):
        current = self.table_view.currentIndex()
        if not current.isValid():
            QMessageBox.warning(self, "警告", f"{self.title}を選択してください")
            return

        master_id = self.model.data(current.siblingAtColumn(0), Qt.UserRole)
        # 役割・作業・習熟度の場合は名前が2列目
        name_col = 1 if self.kind in ['role', 'task', 'proficiency'] else 0
        name = self.model.data(current.siblingAtColumn(name_col), Qt.DisplayRole)

        reply = QMessageBox.question(
            self, "確認",
            f"{self.title}「{name}」を削除しますか？\n"
            "関連するプロジェクトからも削除されます。",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.delete_master(self.kind, master_id)

                self.refresh_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", f"{self.title}を削除しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"削除に失敗しました: {str(e)}")

    def move_up(self):
        """選択されたアイテムを上に移動"""
        current = self.table_view.currentIndex()
        if not current.isValid():
            QMessageBox.warning(self, "警告", f"{self.title}を選択してください")
            return

        current_row = current.row()
        master_id = self.model.data(current.siblingAtColumn(0), Qt.UserRole)

        try:
            with db_service.session_scope() as session:
                repo = Repository(session)
                if repo.move_master_up(self.kind, master_id):
                    self.refresh_data()
                    self.data_changed.emit()
                    # 上に移動したので、移動後は1つ上の行になる
                    new_row = max(0, current_row - 1)
                    # IDで選択を復元
                    for row in range(self.model.rowCount()):
                        if self.model.data(self.model.index(row, 0), Qt.UserRole) == master_id:
                            self.table_view.selectRow(row)
                            break
                else:
                    QMessageBox.information(self, "情報", "これ以上上に移動できません")
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"移動に失敗しました: {str(e)}")

    def move_down(self):
        """選択されたアイテムを下に移動"""
        current = self.table_view.currentIndex()
        if not current.isValid():
            QMessageBox.warning(self, "警告", f"{self.title}を選択してください")
            return

        current_row = current.row()
        master_id = self.model.data(current.siblingAtColumn(0), Qt.UserRole)

        try:
            with db_service.session_scope() as session:
                repo = Repository(session)
                if repo.move_master_down(self.kind, master_id):
                    self.refresh_data()
                    self.data_changed.emit()
                    # 下に移動したので、移動後は1つ下の行になる
                    new_row = min(self.model.rowCount() - 1, current_row + 1)
                    # IDで選択を復元
                    for row in range(self.model.rowCount()):
                        if self.model.data(self.model.index(row, 0), Qt.UserRole) == master_id:
                            self.table_view.selectRow(row)
                            break
                else:
                    QMessageBox.information(self, "情報", "これ以上下に移動できません")
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"移動に失敗しました: {str(e)}")

class MastersView(QWidget):
    data_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        categories = [
            ('os', 'OS'),
            ('language', '言語'),
            ('framework', 'FW/ライブラリ'),
            ('tool', 'ツール'),
            ('cloud', 'クラウド'),
            ('db', 'データベース'),
            ('qualification', '資格'),
            ('role', '役割'),
            ('task', '作業担当'),
            ('proficiency', '習熟度')
        ]
        
        for kind, title in categories:
            tab = MasterTabWidget(kind, title)
            tab.data_changed.connect(self.on_data_changed)
            self.tab_widget.addTab(tab, title)
    
    def on_data_changed(self):
        self.data_changed.emit()