from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableView, QPushButton, QLineEdit, QTextEdit,
    QLabel, QMessageBox, QDialog, QDialogButtonBox,
    QFormLayout, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List
from services.db import db_service
from services.repository import Repository

class MasterTableModel(QAbstractTableModel):
    def __init__(self, kind, data=None):
        super().__init__()
        self.kind = kind
        self.data_list = []
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
            self.data_list.append({
                'id': item.id,
                'name': item.name,
                'note': item.note
            })
        self.endResetModel()

class MasterEditDialog(QDialog):
    def __init__(self, kind, master_id=None, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.master_id = master_id
        self.setWindowTitle("マスタ編集" if master_id else "マスタ追加")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QFormLayout(self)
        
        self.name_edit = QLineEdit()
        layout.addRow("名称:", self.name_edit)
        
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(80)
        layout.addRow("備考:", self.note_edit)
        
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
        return {
            'name': self.name_edit.text().strip(),
            'note': self.note_edit.toPlainText() or None
        }

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
        self.add_button.clicked.connect(self.add_master)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("編集")
        self.edit_button.clicked.connect(self.edit_master)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("削除")
        self.delete_button.clicked.connect(self.delete_master)
        button_layout.addWidget(self.delete_button)
        
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
                    repo.create_master(self.kind, data['name'], data['note'])
                
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
                    repo.update_master(self.kind, master_id, data['name'], data['note'])
                
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
        name = self.model.data(current.siblingAtColumn(0), Qt.DisplayRole)
        
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
            ('role', '役割'),
            ('task', '作業担当')
        ]
        
        for kind, title in categories:
            tab = MasterTabWidget(kind, title)
            tab.data_changed.connect(self.on_data_changed)
            self.tab_widget.addTab(tab, title)
    
    def on_data_changed(self):
        self.data_changed.emit()