"""
アプリケーション共通スタイル定義
"""

# 落ち着いたカラーパレット
COLORS = {
    'primary': '#4a5568',      # グレーブルー
    'primary_dark': '#2d3748',  # ダークグレー
    'secondary': '#38a169',    # 落ち着いたグリーン
    'danger': '#e53e3e',       # 落ち着いたレッド
    'warning': '#d69e2e',      # 落ち着いたオレンジ
    'info': '#3182ce',         # 落ち着いたブルー
    'dark': '#2d3748',         # ダークグレー
    'light': '#f7fafc',        # 非常に薄いグレー
    'border': '#e2e8f0',       # 薄いグレーボーダー
    'text': '#2d3748',         # ダークグレーテキスト
    'text_secondary': '#718096', # グレーテキスト
    'background': '#ffffff',    # 背景白
    'background_alt': '#edf2f7', # 薄いグレー背景
}

# アプリケーション全体のスタイルシート
APP_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}

/* タブウィジェット */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['background']};
    border-radius: 4px;
}}

QTabBar::tab {{
    background-color: {COLORS['background_alt']};
    color: {COLORS['text_secondary']};
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['primary_dark']};
    color: white;
}}

/* プッシュボタン */
QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['dark']};
}}

QPushButton:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['text_secondary']};
}}

/* 削除ボタン */
QPushButton[objectName="deleteButton"] {{
    background-color: {COLORS['danger']};
}}

QPushButton[objectName="deleteButton"]:hover {{
    background-color: #dc2626;
}}

/* セカンダリボタン */
QPushButton[objectName="secondaryButton"] {{
    background-color: {COLORS['background']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
}}

QPushButton[objectName="secondaryButton"]:hover {{
    background-color: {COLORS['background_alt']};
}}

/* ラベル */
QLabel {{
    color: {COLORS['text']};
    font-size: 13px;
}}

QLabel[objectName="titleLabel"] {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS['dark']};
    padding: 10px 0;
}}

QLabel[objectName="sectionLabel"] {{
    font-size: 14px;
    font-weight: 600;
    color: {COLORS['text']};
    padding: 5px 0;
}}

/* 入力フィールド */
QLineEdit, QTextEdit, QPlainTextEdit {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
    background-color: {COLORS['background']};
    color: {COLORS['text']};
    font-size: 13px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['primary']};
    outline: none;
}}

/* リストウィジェット */
QListWidget {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    background-color: {COLORS['background']};
    padding: 4px;
}}

QListWidget::item {{
    padding: 6px;
    border-radius: 4px;
    margin: 2px;
}}

QListWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

QListWidget::item:hover {{
    background-color: {COLORS['background_alt']};
}}

/* テーブルビュー */
QTableView {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    background-color: {COLORS['background']};
    gridline-color: {COLORS['border']};
}}

QTableView::item {{
    padding: 8px;
}}

QTableView::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

QHeaderView::section {{
    background-color: {COLORS['background_alt']};
    color: {COLORS['text']};
    padding: 8px;
    border: none;
    font-weight: 600;
}}

/* コンボボックス */
QComboBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 8px;
    background-color: {COLORS['background']};
    color: {COLORS['text']};
    font-size: 13px;
}}

QComboBox:focus {{
    border-color: {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {COLORS['text_secondary']};
    margin-right: 5px;
}}

/* グループボックス */
QGroupBox {{
    font-weight: 600;
    font-size: 14px;
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    background-color: {COLORS['background']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px 0 8px;
    background-color: {COLORS['background']};
}}

/* スクロールバー */
QScrollBar:vertical {{
    background: {COLORS['background_alt']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_secondary']};
}}

/* DateEdit */
QDateEdit {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 8px;
    background-color: {COLORS['background']};
    color: {COLORS['text']};
    font-size: 13px;
}}

QDateEdit:focus {{
    border-color: {COLORS['primary']};
}}

/* メニューバー */
QMenuBar {{
    background-color: {COLORS['background']};
    border-bottom: 1px solid {COLORS['border']};
}}

QMenuBar::item {{
    padding: 8px 12px;
    background: transparent;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['background_alt']};
}}

/* ステータスバー */
QStatusBar {{
    background-color: {COLORS['background_alt']};
    border-top: 1px solid {COLORS['border']};
    color: {COLORS['text_secondary']};
    font-size: 12px;
}}

/* スプリッター */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:hover {{
    background-color: {COLORS['primary']};
}}
"""

# ボタンのスタイルクラス
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_dark']};
        }}
    """,
    
    'success': f"""
        QPushButton {{
            background-color: {COLORS['secondary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: #059669;
        }}
    """,
    
    'danger': f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: #dc2626;
        }}
    """,
    
    'secondary': f"""
        QPushButton {{
            background-color: {COLORS['background']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['border']};
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['background_alt']};
            border-color: {COLORS['text_secondary']};
        }}
    """
}