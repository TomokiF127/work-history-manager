#!/usr/bin/env python3
"""
技術マスタにproficiency_idカラムを追加するマイグレーションスクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "app"))

import sqlite3
from config import config

def migrate_add_proficiency_columns():
    """技術マスタテーブルにproficiency_idカラムを追加"""

    # データベースファイルのパスを取得
    db_path = config.get_database_path()
    from pathlib import Path
    if not Path(db_path).is_absolute():
        project_root = Path(__file__).parent
        db_path = project_root / db_path

    print(f"データベース: {db_path}")

    # SQLite接続
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 追加するテーブル
    tables = ['oses', 'languages', 'frameworks', 'tools', 'clouds', 'dbs']

    for table in tables:
        # カラムが既に存在するか確認
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]

        if 'proficiency_id' not in columns:
            print(f"{table}テーブルにproficiency_idカラムを追加中...")
            cursor.execute(f"""
                ALTER TABLE {table}
                ADD COLUMN proficiency_id INTEGER
                REFERENCES proficiency_levels(id)
            """)
            print(f"  ✓ {table}テーブルにカラムを追加しました")
        else:
            print(f"  - {table}テーブルには既にproficiency_idカラムが存在します")

    # 変更をコミット
    conn.commit()
    conn.close()

    print("\nマイグレーション完了")

if __name__ == "__main__":
    migrate_add_proficiency_columns()
