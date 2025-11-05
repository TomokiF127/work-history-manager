#!/usr/bin/env python3
"""
習熟度レベルの初期データを投入するスクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "app"))

from services.db import db_service
from services.repository import Repository

def insert_proficiencies():
    """習熟度レベルの初期データを投入"""
    proficiencies = [
        "学習レベル",
        "簡単な操作可能",
        "調べながら操作可能",
        "テスト実行可能",
        "ローカル検証用として利用",
        "テスト用環境として利用可能",
        "基本的なSQL文の使用可能",
        "基本的なDB操作が可能",
        "基本的な操作および調べながら開発可能",
        "調べながら開発可能",
        "設計から開発まで開発可能",
        "通常使用に問題なし"
    ]

    with db_service.session_scope() as session:
        repo = Repository(session)

        # 既存の習熟度レベルを取得
        existing = repo.get_master_by_kind('proficiency')
        existing_names = {prof.name for prof in existing}

        added_count = 0
        for prof_name in proficiencies:
            if prof_name not in existing_names:
                repo.create_master('proficiency', prof_name, None)
                print(f"追加: {prof_name}")
                added_count += 1
            else:
                print(f"スキップ（既存）: {prof_name}")

        print(f"\n合計 {added_count} 件の習熟度レベルを追加しました")

if __name__ == "__main__":
    insert_proficiencies()
