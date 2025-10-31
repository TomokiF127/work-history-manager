from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, 
    QListWidgetItem, QTextEdit, QLineEdit, QLabel, QDialog, 
    QDialogButtonBox, QFormLayout, QMessageBox, QSplitter,
    QAbstractItemView, QGroupBox, QDateEdit, QComboBox
)
from PySide6.QtCore import Qt, QDate, Signal
from datetime import date
from services.db import db_service
from services.repository import Repository
from ui.styles import BUTTON_STYLES

class CombinedPRDialog(QDialog):
    """自己PR・その他経歴統合編集ダイアログ"""
    
    def __init__(self, item_type="pr", item_data=None, parent=None):
        super().__init__(parent)
        self.item_type = item_type  # "pr" or "experience"
        self.item_data = item_data
        self.setWindowTitle("自己PR編集" if item_type == "pr" else "その他経歴編集")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        
        if item_data:
            self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # タイトル
        self.title_edit = QLineEdit()
        if self.item_type == "pr":
            self.title_edit.setPlaceholderText("例: リーダー経験、技術力、チームワーク等")
        else:
            self.title_edit.setPlaceholderText("例: 新技術研修、資格取得、自主学習等")
        form_layout.addRow("タイトル:", self.title_edit)
        
        # その他経歴の場合のみ期間入力を表示
        if self.item_type == "experience":
            # 期間
            period_layout = QHBoxLayout()
            
            # 年選択
            self.start_year_combo = QComboBox()
            self.start_month_combo = QComboBox()
            self.end_year_combo = QComboBox()
            self.end_month_combo = QComboBox()
            
            # 年月の選択肢を設定
            current_year = QDate.currentDate().year()
            for combo in [self.start_year_combo, self.end_year_combo]:
                combo.addItem("未設定", None)
                for year in range(current_year - 20, current_year + 2):
                    combo.addItem(f"{year}年", year)
                combo.setCurrentIndex(0)
            
            for combo in [self.start_month_combo, self.end_month_combo]:
                combo.addItem("未設定", None)
                for month in range(1, 13):
                    combo.addItem(f"{month}月", month)
                combo.setCurrentIndex(0)
            
            period_layout.addWidget(QLabel("開始:"))
            period_layout.addWidget(self.start_year_combo)
            period_layout.addWidget(self.start_month_combo)
            period_layout.addWidget(QLabel("〜"))
            period_layout.addWidget(QLabel("終了:"))
            period_layout.addWidget(self.end_year_combo)
            period_layout.addWidget(self.end_month_combo)
            period_layout.addStretch()
            
            form_layout.addRow("期間:", period_layout)
        
        # 内容
        self.content_edit = QTextEdit()
        if self.item_type == "pr":
            self.content_edit.setPlaceholderText("自己PRの内容を入力してください...")
        else:
            self.content_edit.setPlaceholderText("学習内容や経歴の詳細を入力してください...")
        self.content_edit.setMinimumHeight(200)
        form_layout.addRow("内容:", self.content_edit)
        
        # その他経歴の場合のみ備考を表示
        if self.item_type == "experience":
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
        self.title_edit.setText(self.item_data.title)
        self.content_edit.setPlainText(self.item_data.content)
        
        if self.item_type == "experience":
            # 期間設定
            if hasattr(self.item_data, 'start_date') and self.item_data.start_date:
                for i in range(self.start_year_combo.count()):
                    if self.start_year_combo.itemData(i) == self.item_data.start_date.year:
                        self.start_year_combo.setCurrentIndex(i)
                        break
                for i in range(self.start_month_combo.count()):
                    if self.start_month_combo.itemData(i) == self.item_data.start_date.month:
                        self.start_month_combo.setCurrentIndex(i)
                        break
            
            if hasattr(self.item_data, 'end_date') and self.item_data.end_date:
                for i in range(self.end_year_combo.count()):
                    if self.end_year_combo.itemData(i) == self.item_data.end_date.year:
                        self.end_year_combo.setCurrentIndex(i)
                        break
                for i in range(self.end_month_combo.count()):
                    if self.end_month_combo.itemData(i) == self.item_data.end_date.month:
                        self.end_month_combo.setCurrentIndex(i)
                        break
            
            if hasattr(self.item_data, 'note'):
                self.note_edit.setPlainText(self.item_data.note or "")
    
    def get_data(self):
        """入力データを取得"""
        data = {
            'title': self.title_edit.text().strip(),
            'content': self.content_edit.toPlainText().strip()
        }
        
        if self.item_type == "experience":
            # 期間処理
            start_year = self.start_year_combo.currentData()
            start_month = self.start_month_combo.currentData()
            end_year = self.end_year_combo.currentData()
            end_month = self.end_month_combo.currentData()
            
            if start_year and start_month:
                data['start_date'] = date(start_year, start_month, 1)
            else:
                data['start_date'] = None
                
            if end_year and end_month:
                data['end_date'] = date(end_year, end_month, 1)
            else:
                data['end_date'] = None
            
            data['note'] = self.note_edit.toPlainText() or None
        
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

class CombinedPRView(QWidget):
    """自己PR・その他経歴統合ビュー"""
    
    data_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_item_id = None
        self.current_item_type = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(5)
        
        # タイトル
        title_label = QLabel("自己PR・その他経歴管理")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # 縦分割のメインスプリッター
        main_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(main_splitter)
        
        # === 上側エリア: 自己PR ===
        pr_section = QWidget()
        pr_layout = QVBoxLayout(pr_section)
        pr_layout.setContentsMargins(5, 5, 5, 5)
        
        # 自己PRセクションヘッダー
        pr_header_layout = QHBoxLayout()
        pr_title = QLabel("自己PR管理")
        pr_title.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            color: #2d3748;
            padding: 8px 12px;
            background-color: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
        """)
        pr_header_layout.addWidget(pr_title)
        pr_header_layout.addStretch()
        
        self.new_pr_button = QPushButton("追加")
        self.new_pr_button.setStyleSheet(BUTTON_STYLES['success'])
        self.new_pr_button.clicked.connect(self.new_pr)
        pr_header_layout.addWidget(self.new_pr_button)
        
        pr_layout.addLayout(pr_header_layout)
        
        # 自己PRリストとプレビューの横分割
        pr_splitter = QSplitter(Qt.Horizontal)
        
        # 自己PRリスト側
        pr_left = QWidget()
        pr_left_layout = QVBoxLayout(pr_left)
        pr_left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.pr_list = QListWidget()
        self.pr_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.pr_list.itemSelectionChanged.connect(self.on_pr_selected)
        self.pr_list.itemDoubleClicked.connect(self.edit_pr)
        self.pr_list.setMinimumHeight(150)
        pr_left_layout.addWidget(self.pr_list)
        
        # 自己PRボタン
        pr_button_layout = QHBoxLayout()
        self.edit_pr_button = QPushButton("編集")
        self.edit_pr_button.setStyleSheet(BUTTON_STYLES['primary'])
        self.edit_pr_button.clicked.connect(self.edit_pr)
        self.edit_pr_button.setEnabled(False)
        
        self.delete_pr_button = QPushButton("削除")
        self.delete_pr_button.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_pr_button.clicked.connect(self.delete_pr)
        self.delete_pr_button.setEnabled(False)
        
        pr_button_layout.addWidget(self.edit_pr_button)
        pr_button_layout.addWidget(self.delete_pr_button)
        pr_button_layout.addStretch()
        pr_left_layout.addLayout(pr_button_layout)
        
        # 自己PRプレビュー側
        pr_right = QWidget()
        pr_right_layout = QVBoxLayout(pr_right)
        pr_right_layout.setContentsMargins(5, 0, 0, 0)
        
        self.pr_title_label = QLabel("項目を選択してください")
        self.pr_title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        pr_right_layout.addWidget(self.pr_title_label)
        
        self.pr_content_display = QTextEdit()
        self.pr_content_display.setReadOnly(True)
        self.pr_content_display.setMinimumHeight(150)
        self.pr_content_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                background-color: #fafafa;
                font-size: 9pt;
            }
        """)
        pr_right_layout.addWidget(self.pr_content_display)
        
        pr_splitter.addWidget(pr_left)
        pr_splitter.addWidget(pr_right)
        pr_splitter.setSizes([300, 400])
        pr_layout.addWidget(pr_splitter)
        
        # === 下側エリア: その他経歴 ===
        exp_section = QWidget()
        exp_layout = QVBoxLayout(exp_section)
        exp_layout.setContentsMargins(5, 5, 5, 5)
        
        # その他経歴セクションヘッダー
        exp_header_layout = QHBoxLayout()
        exp_title = QLabel("その他経歴管理")
        exp_title.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            color: #2d3748;
            padding: 8px 12px;
            background-color: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
        """)
        exp_header_layout.addWidget(exp_title)
        exp_header_layout.addStretch()
        
        self.new_experience_button = QPushButton("追加")
        self.new_experience_button.setStyleSheet(BUTTON_STYLES['success'])
        self.new_experience_button.clicked.connect(self.new_experience)
        exp_header_layout.addWidget(self.new_experience_button)
        
        exp_layout.addLayout(exp_header_layout)
        
        # その他経歴リストとプレビューの横分割
        exp_splitter = QSplitter(Qt.Horizontal)
        
        # その他経歴リスト側
        exp_left = QWidget()
        exp_left_layout = QVBoxLayout(exp_left)
        exp_left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.exp_list = QListWidget()
        self.exp_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.exp_list.itemSelectionChanged.connect(self.on_exp_selected)
        self.exp_list.itemDoubleClicked.connect(self.edit_experience)
        self.exp_list.setMinimumHeight(150)
        exp_left_layout.addWidget(self.exp_list)
        
        # その他経歴ボタン
        exp_button_layout = QHBoxLayout()
        self.edit_exp_button = QPushButton("編集")
        self.edit_exp_button.setStyleSheet(BUTTON_STYLES['primary'])
        self.edit_exp_button.clicked.connect(self.edit_experience)
        self.edit_exp_button.setEnabled(False)
        
        self.delete_exp_button = QPushButton("削除")
        self.delete_exp_button.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_exp_button.clicked.connect(self.delete_experience)
        self.delete_exp_button.setEnabled(False)
        
        exp_button_layout.addWidget(self.edit_exp_button)
        exp_button_layout.addWidget(self.delete_exp_button)
        exp_button_layout.addStretch()
        exp_left_layout.addLayout(exp_button_layout)
        
        # その他経歴プレビュー側
        exp_right = QWidget()
        exp_right_layout = QVBoxLayout(exp_right)
        exp_right_layout.setContentsMargins(5, 0, 0, 0)
        
        self.exp_title_label = QLabel("項目を選択してください")
        self.exp_title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        exp_right_layout.addWidget(self.exp_title_label)
        
        self.exp_period_label = QLabel("")
        self.exp_period_label.setStyleSheet("font-size: 10px; color: #666;")
        exp_right_layout.addWidget(self.exp_period_label)
        
        self.exp_content_display = QTextEdit()
        self.exp_content_display.setReadOnly(True)
        self.exp_content_display.setMinimumHeight(120)
        self.exp_content_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                background-color: #fafafa;
                font-size: 9pt;
            }
        """)
        exp_right_layout.addWidget(self.exp_content_display)
        
        exp_splitter.addWidget(exp_left)
        exp_splitter.addWidget(exp_right)
        exp_splitter.setSizes([300, 400])
        exp_layout.addWidget(exp_splitter)
        
        # メインスプリッターに追加
        main_splitter.addWidget(pr_section)
        main_splitter.addWidget(exp_section)
        main_splitter.setSizes([350, 350])  # 上下の高さを拡大
    
    def load_data(self):
        """データを読み込み"""
        with db_service.session_scope() as session:
            repo = Repository(session)
            
            # 自己PRデータを読み込み
            prs = repo.get_all_self_prs()
            self.pr_list.clear()
            for pr in prs:
                item = QListWidgetItem(pr.title)
                item.setData(Qt.UserRole, pr.id)
                self.pr_list.addItem(item)
            
            # その他経歴データを読み込み
            experiences = repo.get_all_other_experiences()
            self.exp_list.clear()
            for exp in experiences:
                period_text = ""
                if exp.start_date or exp.end_date:
                    start = exp.start_date.strftime("%Y/%m") if exp.start_date else "不明"
                    end = exp.end_date.strftime("%Y/%m") if exp.end_date else "継続中"
                    period_text = f" ({start}〜{end})"
                
                item = QListWidgetItem(f"{exp.title}{period_text}")
                item.setData(Qt.UserRole, exp.id)
                self.exp_list.addItem(item)
    
    def on_pr_selected(self):
        """自己PR選択時の処理"""
        current_item = self.pr_list.currentItem()
        if not current_item:
            self.edit_pr_button.setEnabled(False)
            self.delete_pr_button.setEnabled(False)
            self.pr_title_label.setText("項目を選択してください")
            self.pr_content_display.clear()
            return
        
        self.edit_pr_button.setEnabled(True)
        self.delete_pr_button.setEnabled(True)
        
        # プレビューを更新
        self.update_pr_preview()
    
    def on_exp_selected(self):
        """その他経歴選択時の処理"""
        current_item = self.exp_list.currentItem()
        if not current_item:
            self.edit_exp_button.setEnabled(False)
            self.delete_exp_button.setEnabled(False)
            self.exp_title_label.setText("項目を選択してください")
            self.exp_period_label.setText("")
            self.exp_content_display.clear()
            return
        
        self.edit_exp_button.setEnabled(True)
        self.delete_exp_button.setEnabled(True)
        
        # プレビューを更新
        self.update_exp_preview()
    
    def update_pr_preview(self):
        """自己PRプレビューを更新"""
        current_item = self.pr_list.currentItem()
        if not current_item:
            return
        
        pr_id = current_item.data(Qt.UserRole)
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            pr = repo.get_self_pr_by_id(pr_id)
            if pr:
                self.pr_title_label.setText(pr.title)
                self.pr_content_display.setText(pr.content)
    
    def update_exp_preview(self):
        """その他経歴プレビューを更新"""
        current_item = self.exp_list.currentItem()
        if not current_item:
            return
        
        exp_id = current_item.data(Qt.UserRole)
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            exp = repo.get_other_experience_by_id(exp_id)
            if exp:
                self.exp_title_label.setText(exp.title)
                
                # 期間表示
                period_text = ""
                if exp.start_date or exp.end_date:
                    start = exp.start_date.strftime("%Y年%m月") if exp.start_date else "不明"
                    end = exp.end_date.strftime("%Y年%m月") if exp.end_date else "継続中"
                    period_text = f"期間: {start} 〜 {end}"
                
                self.exp_period_label.setText(period_text)
                self.exp_content_display.setText(exp.content)
    
    def new_pr(self):
        """新しい自己PRを追加"""
        dialog = CombinedPRDialog("pr", parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    
                    # 新しい順序インデックスを設定
                    prs = repo.get_all_self_prs()
                    data['order_index'] = len(prs)
                    
                    repo.create_self_pr(data)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "自己PRを追加しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"追加に失敗しました: {str(e)}")
    
    def new_experience(self):
        """新しいその他経歴を追加"""
        dialog = CombinedPRDialog("experience", parent=self)
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
    
    def edit_pr(self):
        """自己PRを編集"""
        current_item = self.pr_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "自己PRを選択してください")
            return
        
        pr_id = current_item.data(Qt.UserRole)
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            pr = repo.get_self_pr_by_id(pr_id)
            
            if not pr:
                return
            
            dialog = CombinedPRDialog("pr", pr, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                try:
                    repo.update_self_pr(pr_id, data)
                    
                    self.load_data()
                    self.data_changed.emit()
                    self.update_pr_preview()
                    QMessageBox.information(self, "成功", "自己PRを更新しました")
                except Exception as e:
                    QMessageBox.critical(self, "エラー", f"更新に失敗しました: {str(e)}")
    
    def edit_experience(self):
        """その他経歴を編集"""
        current_item = self.exp_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "その他経歴を選択してください")
            return
        
        exp_id = current_item.data(Qt.UserRole)
        
        with db_service.session_scope() as session:
            repo = Repository(session)
            exp = repo.get_other_experience_by_id(exp_id)
            
            if not exp:
                return
            
            dialog = CombinedPRDialog("experience", exp, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                try:
                    repo.update_other_experience(exp_id, data)
                    
                    self.load_data()
                    self.data_changed.emit()
                    self.update_exp_preview()
                    QMessageBox.information(self, "成功", "その他経歴を更新しました")
                except Exception as e:
                    QMessageBox.critical(self, "エラー", f"更新に失敗しました: {str(e)}")
    
    def delete_pr(self):
        """自己PRを削除"""
        current_item = self.pr_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "自己PRを選択してください")
            return
        
        reply = QMessageBox.question(
            self, "確認",
            f"自己PR「{current_item.text()}」を削除しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            pr_id = current_item.data(Qt.UserRole)
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.delete_self_pr(pr_id)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "自己PRを削除しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"削除に失敗しました: {str(e)}")
    
    def delete_experience(self):
        """その他経歴を削除"""
        current_item = self.exp_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "その他経歴を選択してください")
            return
        
        reply = QMessageBox.question(
            self, "確認",
            f"その他経歴「{current_item.text()}」を削除しますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            exp_id = current_item.data(Qt.UserRole)
            try:
                with db_service.session_scope() as session:
                    repo = Repository(session)
                    repo.delete_other_experience(exp_id)
                
                self.load_data()
                self.data_changed.emit()
                QMessageBox.information(self, "成功", "その他経歴を削除しました")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"削除に失敗しました: {str(e)}")
    
