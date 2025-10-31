from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, 
    QListWidgetItem, QTextEdit, QLineEdit, QLabel, QDialog, 
    QDialogButtonBox, QFormLayout, QMessageBox, QSplitter,
    QAbstractItemView, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from services.db import db_service
from services.repository import Repository
from ui.styles import BUTTON_STYLES

class SelfPRDialog(QDialog):
    """自己PR編集ダイアログ"""
    
    def __init__(self, pr_data=None, parent=None):
        super().__init__(parent)
        self.pr_data = pr_data
        self.setWindowTitle("自己PR編集")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        
        if pr_data:
            self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # タイトル
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("例: リーダー経験、技術力、チームワーク等")
        form_layout.addRow("タイトル:", self.title_edit)
        
        # 内容
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("自己PRの内容を入力してください...")
        self.content_edit.setMinimumHeight(200)
        form_layout.addRow("内容:", self.content_edit)
        
        layout.addLayout(form_layout)
        
        # ボタン
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_data(self):
        """既存データを読み込み"""
        self.title_edit.setText(self.pr_data.title)
        self.content_edit.setPlainText(self.pr_data.content)
    
    def get_data(self):
        """入力データを取得"""
        return {
            'title': self.title_edit.text().strip(),
            'content': self.content_edit.toPlainText().strip()
        }
    
    def accept(self):
        """OKボタン押下時の検証"""
        data = self.get_data()
        if not data['title']:
            QMessageBox.warning(self, "入力エラー", "タイトルを入力してください。")
            return
        if not data['content']:
            QMessageBox.warning(self, "入力エラー", "内容を入力してください。")
            return
        
        super().accept()

class SelfPRView(QWidget):
    """自己PR管理ビュー"""
    
    data_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_pr_id = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)  # 上の余白を小さく
        layout.setSpacing(10)  # 要素間の間隔を調整
        
        # タイトル
        title_label = QLabel("自己PR管理")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # メインレイアウト
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左側: リスト
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # リスト
        list_group = QGroupBox("自己PRリスト")
        list_layout = QVBoxLayout(list_group)
        
        self.pr_list = QListWidget()
        self.pr_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.pr_list.itemSelectionChanged.connect(self.on_pr_selected)
        self.pr_list.itemDoubleClicked.connect(self.edit_pr)  # ダブルクリックで編集
        list_layout.addWidget(self.pr_list)
        
        left_layout.addWidget(list_group)
        
        # ボタンをグループ化
        button_group = QGroupBox("操作")
        button_group_layout = QVBoxLayout(button_group)
        
        # 追加・編集・削除ボタン
        crud_layout = QHBoxLayout()
        
        self.new_button = QPushButton("新規追加")
        self.new_button.setStyleSheet(BUTTON_STYLES['success'])
        self.new_button.setToolTip("新しい自己PR項目を追加します")
        self.new_button.clicked.connect(self.new_pr)
        crud_layout.addWidget(self.new_button)
        
        self.edit_button = QPushButton("編集")
        self.edit_button.setStyleSheet(BUTTON_STYLES['primary'])
        self.edit_button.setToolTip("選択した項目を編集します（ダブルクリックでも可）")
        self.edit_button.clicked.connect(self.edit_pr)
        self.edit_button.setEnabled(False)
        crud_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("削除")
        self.delete_button.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_button.setToolTip("選択した項目を削除します")
        self.delete_button.clicked.connect(self.delete_pr)
        self.delete_button.setEnabled(False)
        crud_layout.addWidget(self.delete_button)
        
        button_group_layout.addLayout(crud_layout)
        
        # 順序変更ボタン
        order_layout = QHBoxLayout()
        order_layout.addWidget(QLabel("表示順序:"))
        
        self.up_button = QPushButton("上に移動")
        self.up_button.setStyleSheet(BUTTON_STYLES['secondary'])
        self.up_button.setToolTip("選択した項目を上に移動します")
        self.up_button.clicked.connect(self.move_up)
        self.up_button.setEnabled(False)
        order_layout.addWidget(self.up_button)
        
        self.down_button = QPushButton("下に移動")
        self.down_button.setStyleSheet(BUTTON_STYLES['secondary'])
        self.down_button.setToolTip("選択した項目を下に移動します")
        self.down_button.clicked.connect(self.move_down)
        self.down_button.setEnabled(False)
        order_layout.addWidget(self.down_button)
        
        button_group_layout.addLayout(order_layout)
        left_layout.addWidget(button_group)
        
        # 右側: プレビュー
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        preview_group = QGroupBox("プレビュー（スキルシート出力イメージ）")
        preview_layout = QVBoxLayout(preview_group)
        
        # タイトル表示
        title_container = QHBoxLayout()
        title_container.addWidget(QLabel("◆"))
        self.title_label = QLabel("項目を選択してください")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        title_container.addWidget(self.title_label)
        title_container.addStretch()
        preview_layout.addLayout(title_container)
        
        # 内容表示
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: #fafafa;
                font-family: 'MS ゴシック', 'MS Gothic', monospace;
                font-size: 10pt;
                line-height: 1.4;
            }
        """)
        self.content_display.setPlaceholderText("選択した自己PR項目の内容がここに表示されます。\n\nスキルシート出力時のイメージを確認できます。")
        preview_layout.addWidget(self.content_display)
        
        # ヒント表示
        hint_label = QLabel("💡 ヒント: 項目をダブルクリックすると編集できます")
        hint_label.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        preview_layout.addWidget(hint_label)
        
        right_layout.addWidget(preview_group)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 550])
    
    def load_data(self):
        """データを読み込み"""
        self.pr_list.clear()
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            prs = repo.get_all_self_prs()
            
            for pr in prs:
                item = QListWidgetItem(pr.title)
                item.setData(Qt.UserRole, pr.id)
                self.pr_list.addItem(item)
    
    def on_pr_selected(self):
        """自己PR選択時の処理"""
        current = self.pr_list.currentItem()
        
        if current:
            self.current_pr_id = current.data(Qt.UserRole)
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.up_button.setEnabled(True)
            self.down_button.setEnabled(True)
            
            # プレビュー表示
            with db_service.session_scope() as session:
                repo = Repository(session)
                pr = repo.get_self_pr_by_id(self.current_pr_id)
                
                if pr:
                    self.title_label.setText(pr.title)
                    self.content_display.setPlainText(pr.content)
        else:
            self.current_pr_id = None
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.up_button.setEnabled(False)
            self.down_button.setEnabled(False)
            
            self.title_label.setText("項目を選択してください")
            self.content_display.clear()
    
    def new_pr(self):
        """新規自己PR作成"""
        dialog = SelfPRDialog(parent=self)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # 順序を設定（最後に追加）
            data['order_index'] = self.pr_list.count()
            
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.create_self_pr(data)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "自己PRを作成しました。")
                
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"自己PRの作成に失敗しました:\n{str(e)}")
    
    def edit_pr(self):
        """自己PR編集"""
        if not self.current_pr_id:
            return
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            pr = repo.get_self_pr_by_id(self.current_pr_id)
            
            if not pr:
                QMessageBox.warning(self, "エラー", "自己PRが見つかりません。")
                return
            
            dialog = SelfPRDialog(pr_data=pr, parent=self)
            
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                
                try:
                    repo.update_self_pr(self.current_pr_id, data)
                    
                    self.load_data()
                    self.data_changed.emit()
                    QMessageBox.information(self, "成功", "自己PRを更新しました。")
                    
                except Exception as e:
                    QMessageBox.critical(self, "エラー", f"自己PRの更新に失敗しました:\n{str(e)}")
    
    def delete_pr(self):
        """自己PR削除"""
        if not self.current_pr_id:
            return
        
        reply = QMessageBox.question(
            self, "確認",
            "選択した自己PRを削除しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.delete_self_pr(self.current_pr_id)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "自己PRを削除しました。")
                
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"自己PRの削除に失敗しました:\n{str(e)}")
    
    def move_up(self):
        """順序を上に移動"""
        self._move_item(-1)
    
    def move_down(self):
        """順序を下に移動"""
        self._move_item(1)
    
    def _move_item(self, direction):
        """アイテムの順序を変更"""
        current_row = self.pr_list.currentRow()
        if current_row == -1:
            return
        
        new_row = current_row + direction
        if new_row < 0 or new_row >= self.pr_list.count():
            return
        
        try:
            # 順序更新用のデータを準備
            orders = []
            for i in range(self.pr_list.count()):
                item = self.pr_list.item(i)
                pr_id = item.data(Qt.UserRole)
                
                if i == current_row:
                    orders.append({'id': pr_id, 'order': new_row})
                elif i == new_row:
                    orders.append({'id': pr_id, 'order': current_row})
                else:
                    orders.append({'id': pr_id, 'order': i})
            
            with db_service.session_scope() as session:
                repo = Repository(session)
                repo.reorder_self_prs(orders)
            
            self.load_data()
            
            # 移動後の選択を維持
            self.pr_list.setCurrentRow(new_row)
            self.data_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"順序の変更に失敗しました:\n{str(e)}")