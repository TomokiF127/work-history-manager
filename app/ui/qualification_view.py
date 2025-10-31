from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QLabel, QDialog, QDialogButtonBox, QFormLayout, QMessageBox,
    QComboBox, QDateEdit, QTextEdit, QAbstractItemView, QHeaderView
)
from PySide6.QtCore import Qt, QDate, Signal, QAbstractTableModel, QModelIndex
from datetime import date
from services.db import db_service
from services.repository import Repository
from ui.styles import BUTTON_STYLES

class UserQualificationTableModel(QAbstractTableModel):
    def __init__(self, qualifications=None):
        super().__init__()
        self.qualifications = []
        self.headers = ["資格名", "取得年月", "備考"]
        if qualifications:
            self.update_qualifications(qualifications)
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.qualifications)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        qualification = self.qualifications[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:
                return qualification['qualification_name']
            elif col == 1:
                obtained_date = qualification['obtained_date']
                if obtained_date:
                    return obtained_date.strftime("%Y年%m月")
                return ""
            elif col == 2:
                return qualification['note'] or ""
        elif role == Qt.UserRole:
            return qualification['id']
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def update_qualifications(self, qualifications):
        self.beginResetModel()
        self.qualifications = []
        for qual in qualifications:
            self.qualifications.append({
                'id': qual.id,
                'qualification_id': qual.qualification_id,
                'qualification_name': qual.qualification.name,
                'obtained_date': qual.obtained_date,
                'note': qual.note
            })
        self.endResetModel()

class QualificationEditDialog(QDialog):
    def __init__(self, qualification_data=None, parent=None):
        super().__init__(parent)
        self.qualification_data = qualification_data
        self.setWindowTitle("資格取得情報編集")
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()
        
        if qualification_data:
            self.load_data()
    
    def init_ui(self):
        layout = QFormLayout(self)
        
        # 資格選択
        self.qualification_combo = QComboBox()
        self.qualification_combo.setMinimumWidth(300)  # 幅を広げる
        self.load_qualifications()
        layout.addRow("資格:", self.qualification_combo)
        
        # 取得年月（年・月を別々に選択）
        date_layout = QHBoxLayout()
        
        # 年選択
        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 20, current_year + 2):  # 過去20年から未来2年まで
            self.year_combo.addItem(f"{year}年", year)
        self.year_combo.setCurrentText(f"{current_year}年")
        date_layout.addWidget(self.year_combo)
        
        # 月選択
        self.month_combo = QComboBox()
        for month in range(1, 13):
            self.month_combo.addItem(f"{month}月", month)
        self.month_combo.setCurrentText(f"{QDate.currentDate().month()}月")
        date_layout.addWidget(self.month_combo)
        
        date_layout.addStretch()
        layout.addRow("取得年月:", date_layout)
        
        # 備考
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(80)
        self.note_edit.setPlaceholderText("認定番号や備考を入力...")
        layout.addRow("備考:", self.note_edit)
        
        # ボタン
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def load_qualifications(self):
        """資格マスタを読み込み"""
        with db_service.session_scope() as session:
            repo = Repository(session)
            qualifications = repo.get_master_by_kind('qualification')
            
            self.qualification_combo.clear()
            for qual in qualifications:
                self.qualification_combo.addItem(qual.name, qual.id)
    
    def load_data(self):
        """既存データを読み込み"""
        # 資格選択
        for i in range(self.qualification_combo.count()):
            if self.qualification_combo.itemData(i) == self.qualification_data['qualification_id']:
                self.qualification_combo.setCurrentIndex(i)
                break
        
        # 取得年月
        if self.qualification_data['obtained_date']:
            obtained_date = self.qualification_data['obtained_date']
            # 年設定
            for i in range(self.year_combo.count()):
                if self.year_combo.itemData(i) == obtained_date.year:
                    self.year_combo.setCurrentIndex(i)
                    break
            # 月設定
            for i in range(self.month_combo.count()):
                if self.month_combo.itemData(i) == obtained_date.month:
                    self.month_combo.setCurrentIndex(i)
                    break
        
        # 備考
        self.note_edit.setText(self.qualification_data['note'] or "")
    
    def get_data(self):
        """入力データを取得"""
        # 年月から日付を作成（月の1日に設定）
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        obtained_date = date(year, month, 1)
        
        return {
            'qualification_id': self.qualification_combo.currentData(),
            'obtained_date': obtained_date,
            'note': self.note_edit.toPlainText() or None
        }
    
    def accept(self):
        """OKボタン押下時の検証"""
        if self.qualification_combo.currentData() is None:
            QMessageBox.warning(self, "入力エラー", "資格を選択してください。")
            return
        
        super().accept()

class QualificationView(QWidget):
    data_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(10)
        
        # タイトル
        title_label = QLabel("資格取得管理")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # テーブル
        self.table_view = QTableView()
        self.model = UserQualificationTableModel()
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.table_view.doubleClicked.connect(self.edit_qualification)
        layout.addWidget(self.table_view)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("追加")
        self.add_button.setStyleSheet(BUTTON_STYLES['success'])
        self.add_button.clicked.connect(self.add_qualification)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("編集")
        self.edit_button.setStyleSheet(BUTTON_STYLES['primary'])
        self.edit_button.clicked.connect(self.edit_qualification)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("削除")
        self.delete_button.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_button.clicked.connect(self.delete_qualification)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def on_selection_changed(self):
        """選択状態変更時の処理"""
        has_selection = self.table_view.selectionModel().hasSelection()
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def load_data(self):
        """データを読み込み"""
        with db_service.session_scope() as session:
            repo = Repository(session)
            qualifications = repo.get_all_user_qualifications()
            self.model.update_qualifications(qualifications)
    
    def add_qualification(self):
        """資格取得情報を追加"""
        dialog = QualificationEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.create_user_qualification(data)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "資格取得情報を追加しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"追加に失敗しました: {str(e)}")
    
    def edit_qualification(self):
        """資格取得情報を編集"""
        current = self.table_view.currentIndex()
        if not current.isValid():
            QMessageBox.warning(self, "警告", "資格を選択してください")
            return
        
        qualification_id = self.model.data(current.siblingAtColumn(0), Qt.UserRole)
        qualification_data = None
        
        # 現在のデータを取得
        for qual in self.model.qualifications:
            if qual['id'] == qualification_id:
                qualification_data = qual
                break
        
        if not qualification_data:
            return
        
        dialog = QualificationEditDialog(qualification_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.update_user_qualification(qualification_id, data)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "資格取得情報を更新しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"更新に失敗しました: {str(e)}")
    
    def delete_qualification(self):
        """資格取得情報を削除"""
        current = self.table_view.currentIndex()
        if not current.isValid():
            QMessageBox.warning(self, "警告", "資格を選択してください")
            return
        
        qualification_id = self.model.data(current.siblingAtColumn(0), Qt.UserRole)
        qualification_name = self.model.data(current.siblingAtColumn(0), Qt.DisplayRole)
        
        reply = QMessageBox.question(
            self, "確認",
            f"資格取得情報「{qualification_name}」を削除しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.delete_user_qualification(qualification_id)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "資格取得情報を削除しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"削除に失敗しました: {str(e)}")