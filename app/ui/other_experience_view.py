from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, 
    QListWidgetItem, QTextEdit, QLineEdit, QLabel, QDialog, 
    QDialogButtonBox, QFormLayout, QMessageBox, QSplitter,
    QAbstractItemView, QGroupBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate, Signal
from datetime import date
from services.db import db_service
from services.repository import Repository
from ui.styles import BUTTON_STYLES

class OtherExperienceDialog(QDialog):
    """その他経歴編集ダイアログ"""
    
    def __init__(self, experience_data=None, parent=None):
        super().__init__(parent)
        self.experience_data = experience_data
        self.setWindowTitle("その他経歴編集")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        
        if experience_data:
            self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # タイトル
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("例: 新技術研修、資格取得、自主学習等")
        form_layout.addRow("タイトル:", self.title_edit)
        
        # 期間
        period_layout = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy年MM月")
        self.start_date.setSpecialValueText("指定なし")
        period_layout.addWidget(QLabel("開始:"))
        period_layout.addWidget(self.start_date)
        
        period_layout.addWidget(QLabel("〜"))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy年MM月")
        self.end_date.setSpecialValueText("指定なし")
        period_layout.addWidget(QLabel("終了:"))
        period_layout.addWidget(self.end_date)
        
        form_layout.addRow("期間:", period_layout)
        
        # 内容
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("学習内容や経歴の詳細を入力してください...")
        self.content_edit.setMinimumHeight(200)
        form_layout.addRow("内容:", self.content_edit)
        
        # 備考
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(80)
        self.note_edit.setPlaceholderText("備考があれば入力...")
        form_layout.addRow("備考:", self.note_edit)
        
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
        self.title_edit.setText(self.experience_data.title)
        self.content_edit.setPlainText(self.experience_data.content)
        
        if self.experience_data.start_date:
            self.start_date.setDate(QDate.fromString(
                self.experience_data.start_date.strftime('%Y-%m-%d'), 
                'yyyy-MM-dd'
            ))
        
        if self.experience_data.end_date:
            self.end_date.setDate(QDate.fromString(
                self.experience_data.end_date.strftime('%Y-%m-%d'), 
                'yyyy-MM-dd'
            ))
        
        if self.experience_data.note:
            self.note_edit.setPlainText(self.experience_data.note)
    
    def get_data(self):
        """入力データを取得"""
        data = {
            'title': self.title_edit.text().strip(),
            'content': self.content_edit.toPlainText().strip(),
            'note': self.note_edit.toPlainText() or None
        }
        
        # 日付の処理（最小値の場合はNoneにする）
        if self.start_date.date() != self.start_date.minimumDate():
            data['start_date'] = self.start_date.date().toPython()
        else:
            data['start_date'] = None
            
        if self.end_date.date() != self.end_date.minimumDate():
            data['end_date'] = self.end_date.date().toPython()
        else:
            data['end_date'] = None
        
        return data
    
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

class OtherExperienceView(QWidget):
    """その他経歴管理ビュー"""
    
    data_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_experience_id = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(10)
        
        # タイトル
        title_label = QLabel("その他経歴管理")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # メインレイアウト
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左側: リスト
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # リスト
        list_group = QGroupBox("その他経歴リスト")
        list_layout = QVBoxLayout(list_group)
        
        self.experience_list = QListWidget()
        self.experience_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.experience_list.itemSelectionChanged.connect(self.on_experience_selected)
        self.experience_list.itemDoubleClicked.connect(self.edit_experience)
        list_layout.addWidget(self.experience_list)
        
        left_layout.addWidget(list_group)
        
        # ボタンをグループ化
        button_group = QGroupBox("操作")
        button_group_layout = QVBoxLayout(button_group)
        
        # 追加・編集・削除ボタン
        crud_layout = QHBoxLayout()
        
        self.new_button = QPushButton("新規追加")
        self.new_button.setStyleSheet(BUTTON_STYLES['success'])
        self.new_button.setToolTip("新しいその他経歴を追加します")
        self.new_button.clicked.connect(self.new_experience)
        crud_layout.addWidget(self.new_button)
        
        self.edit_button = QPushButton("編集")
        self.edit_button.setStyleSheet(BUTTON_STYLES['primary'])
        self.edit_button.setToolTip("選択した項目を編集します（ダブルクリックでも可）")
        self.edit_button.clicked.connect(self.edit_experience)
        self.edit_button.setEnabled(False)
        crud_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("削除")
        self.delete_button.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_button.setToolTip("選択した項目を削除します")
        self.delete_button.clicked.connect(self.delete_experience)
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
        
        # 期間表示
        self.period_label = QLabel("")
        self.period_label.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 8px;")
        preview_layout.addWidget(self.period_label)
        
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
        self.content_display.setPlaceholderText("選択したその他経歴の内容がここに表示されます。\\n\\nスキルシート出力時のイメージを確認できます。")
        preview_layout.addWidget(self.content_display)
        
        # ヒント表示
        hint_label = QLabel("💡 ヒント: 項目をダブルクリックすると編集できます")
        hint_label.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        preview_layout.addWidget(hint_label)
        
        right_layout.addWidget(preview_group)
        
        # スプリッターに追加
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])
    
    def load_data(self):
        """データを読み込み"""
        with db_service.session_scope() as session:
            repo = Repository(session)
            experiences = repo.get_all_other_experiences()
            
            self.experience_list.clear()
            for experience in experiences:
                item = QListWidgetItem()
                period_text = ""
                if experience.start_date or experience.end_date:
                    start = experience.start_date.strftime("%Y/%m") if experience.start_date else "不明"
                    end = experience.end_date.strftime("%Y/%m") if experience.end_date else "継続中"
                    period_text = f" ({start}〜{end})"
                
                item.setText(f"{experience.title}{period_text}")
                item.setData(Qt.UserRole, experience.id)
                self.experience_list.addItem(item)
    
    def on_experience_selected(self):
        """経歴選択時の処理"""
        current_item = self.experience_list.currentItem()
        if not current_item:
            self.current_experience_id = None
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.up_button.setEnabled(False)
            self.down_button.setEnabled(False)
            self.title_label.setText("項目を選択してください")
            self.period_label.setText("")
            self.content_display.clear()
            return
        
        self.current_experience_id = current_item.data(Qt.UserRole)
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # 移動ボタンの有効/無効を設定
        current_row = self.experience_list.currentRow()
        self.up_button.setEnabled(current_row > 0)
        self.down_button.setEnabled(current_row < self.experience_list.count() - 1)
        
        # プレビューを更新
        self.update_preview()
    
    def update_preview(self):
        """プレビューを更新"""
        if not self.current_experience_id:
            return
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            experience = repo.get_other_experience_by_id(self.current_experience_id)
            
            if experience:
                self.title_label.setText(experience.title)
                
                # 期間表示
                period_text = ""
                if experience.start_date or experience.end_date:
                    start = experience.start_date.strftime("%Y年%m月") if experience.start_date else "不明"
                    end = experience.end_date.strftime("%Y年%m月") if experience.end_date else "継続中"
                    period_text = f"期間: {start} 〜 {end}"
                
                self.period_label.setText(period_text)
                self.content_display.setText(experience.content)
    
    def new_experience(self):
        """新しいその他経歴を追加"""
        dialog = OtherExperienceDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    
                    # 新しい順序インデックスを設定
                    experiences = repo.get_all_other_experiences()
                    data['order_index'] = len(experiences)
                    
                    repo.create_other_experience(data)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "その他経歴を追加しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"追加に失敗しました: {str(e)}")
    
    def edit_experience(self):
        """その他経歴を編集"""
        if not self.current_experience_id:
            QMessageBox.warning(self, "警告", "項目を選択してください")
            return
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            experience = repo.get_other_experience_by_id(self.current_experience_id)
            
            if not experience:
                return
            
            dialog = OtherExperienceDialog(experience, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                try:
                    repo.update_other_experience(self.current_experience_id, data)
                    
                    self.load_data()
                    self.data_changed.emit()
                    self.update_preview()
                    QMessageBox.information(self, "成功", "その他経歴を更新しました")
                except Exception as e:
                    QMessageBox.critical(self, "エラー", f"更新に失敗しました: {str(e)}")
    
    def delete_experience(self):
        """その他経歴を削除"""
        if not self.current_experience_id:
            QMessageBox.warning(self, "警告", "項目を選択してください")
            return
        
        current_item = self.experience_list.currentItem()
        if not current_item:
            return
        
        reply = QMessageBox.question(
            self, "確認",
            f"その他経歴「{current_item.text()}」を削除しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.delete_other_experience(self.current_experience_id)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "その他経歴を削除しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"削除に失敗しました: {str(e)}")
    
    def move_up(self):
        """選択項目を上に移動"""
        self._move_item(-1)
    
    def move_down(self):
        """選択項目を下に移動"""
        self._move_item(1)
    
    def _move_item(self, direction):
        """項目を移動（direction: -1=上, 1=下）"""
        current_row = self.experience_list.currentRow()
        if current_row == -1:
            return
        
        new_row = current_row + direction
        if new_row < 0 or new_row >= self.experience_list.count():
            return
        
        try:
            with db_service.session_scope() as session:
                repo = Repository(session)
                
                # 現在のアイテムと移動先のアイテムのIDを取得
                current_id = self.experience_list.item(current_row).data(Qt.UserRole)
                target_id = self.experience_list.item(new_row).data(Qt.UserRole)
                
                # 順序を入れ替え
                current_exp = repo.get_other_experience_by_id(current_id)
                target_exp = repo.get_other_experience_by_id(target_id)
                
                if current_exp and target_exp:
                    # 順序を交換
                    temp_order = current_exp.order_index
                    current_exp.order_index = target_exp.order_index
                    target_exp.order_index = temp_order
                    
                    session.flush()
            
            # UIを更新
            self.load_data()
            
            # 移動後のアイテムを選択状態に戻す
            for i in range(self.experience_list.count()):
                if self.experience_list.item(i).data(Qt.UserRole) == current_id:
                    self.experience_list.setCurrentRow(i)
                    break
            
            self.data_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"移動に失敗しました: {str(e)}")