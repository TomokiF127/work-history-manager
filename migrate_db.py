#!/usr/bin/env python3
"""
データベースマイグレーションスクリプト
新しいテーブル（qualifications, user_qualifications, other_experiences）を作成
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from models import Base, init_db
from services.db import db_service
from services.repository import Repository

def migrate_database():
    """データベースマイグレーションを実行"""
    print("データベースマイグレーションを開始します...")
    
    try:
        # エンジンとセッションを取得
        engine, _ = init_db()
        
        # 新しいテーブルを作成
        print("新しいテーブルを作成中...")
        Base.metadata.create_all(bind=engine)
        
        # 資格マスタに初期データを投入
        print("資格マスタに初期データを投入中...")
        with db_service.session_scope() as session:
            repo = Repository(session)
            
            # 既存の資格データがあるかチェック
            existing_qualifications = repo.get_master_by_kind('qualification')
            if not existing_qualifications:
                # 初期資格データ
                initial_qualifications = [
                    "基本情報技術者試験",
                    "応用情報技術者試験", 
                    "ITパスポート",
                    "Oracle Bronze",
                    "Oracle Silver",
                    "Oracle Gold",
                    "AWS Cloud Practitioner",
                    "AWS Solutions Architect Associate",
                    "AWS Solutions Architect Professional",
                    "Microsoft Azure Fundamentals",
                    "Google Cloud Associate Cloud Engineer",
                    "LPIC Level1",
                    "LPIC Level2",
                    "LPIC Level3",
                    "Cisco CCNA",
                    "Cisco CCNP",
                    "PMP",
                    "ITIL Foundation",
                    "情報セキュリティマネジメント試験",
                    "情報処理安全確保支援士"
                ]
                
                for qual_name in initial_qualifications:
                    repo.create_master('qualification', qual_name, None)
                
                print(f"資格マスタに {len(initial_qualifications)} 件のデータを追加しました")
            else:
                print("資格マスタは既に存在します")
        
        print("マイグレーション完了!")
        
    except Exception as e:
        print(f"マイグレーション中にエラーが発生しました: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("データベースマイグレーションが正常に完了しました。")
        sys.exit(0)
    else:
        print("データベースマイグレーションに失敗しました。")
        sys.exit(1)