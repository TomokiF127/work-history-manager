#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rolesとtasksテーブルにorder_indexカラムを追加
"""

import sys
sys.path.append('app')

from services.db import db_service
import sqlite3

def add_order_columns():
    """order_indexカラムを追加"""
    try:
        # 直接SQLiteに接続してカラムを追加
        db_path = "data/skills.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("order_indexカラムの追加を開始...")
            
            # rolesテーブルにorder_indexカラムを追加
            try:
                cursor.execute("ALTER TABLE roles ADD COLUMN order_index INTEGER DEFAULT 0")
                print("rolesテーブルにorder_indexカラムを追加しました")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("rolesテーブルのorder_indexカラムは既に存在します")
                else:
                    print(f"rolesテーブル更新エラー: {e}")
            
            # tasksテーブルにorder_indexカラムを追加
            try:
                cursor.execute("ALTER TABLE tasks ADD COLUMN order_index INTEGER DEFAULT 0")
                print("tasksテーブルにorder_indexカラムを追加しました")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("tasksテーブルのorder_indexカラムは既に存在します")
                else:
                    print(f"tasksテーブル更新エラー: {e}")
            
            conn.commit()
            print("データベース更新完了")
            
            # テーブル構造を確認
            print("\nrolesテーブル構造:")
            cursor.execute("PRAGMA table_info(roles)")
            for row in cursor.fetchall():
                print(f"  {row}")
            
            print("\ntasksテーブル構造:")
            cursor.execute("PRAGMA table_info(tasks)")
            for row in cursor.fetchall():
                print(f"  {row}")
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_order_columns()