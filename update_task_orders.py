#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
作業マスタの順序更新とIT開発作業の追加
"""

import sys
sys.path.append('app')

from services.db import db_service
from services.repository import Repository

# IT開発作業を上流から下流順に定義
IT_DEVELOPMENT_TASKS = [
    # 上流工程
    ("要件定義", "システムに求められる機能や制約を明確にする工程", 10),
    ("要件整理", "収集した要件を整理・分析する作業", 20),
    ("企画", "プロジェクトの企画・計画を立案する作業", 30),
    ("基本設計", "システム全体のアーキテクチャを設計する工程", 40),
    ("詳細設計", "基本設計を元に詳細な設計を行う工程", 50),
    ("外部設計", "システムの外部インターフェースを設計", 60),
    ("内部設計", "システムの内部構造を設計", 70),
    ("DB設計", "データベースの設計を行う作業", 80),
    
    # 開発工程
    ("製造", "設計に基づいてプログラムを作成する工程", 90),
    ("実装", "設計に基づいてシステムを実装する作業", 100),
    ("開発", "プログラムの開発・コーディング作業", 110),
    ("コーディング", "プログラムコードの作成作業", 120),
    ("プログラミング", "プログラムの作成・実装作業", 130),
    
    # テスト工程
    ("単体テスト", "個別のモジュールをテストする工程", 140),
    ("結合テスト", "複数のモジュールを結合してテスト", 150),
    ("システムテスト", "システム全体の動作をテスト", 160),
    ("総合テスト", "システム全体の総合的なテスト", 170),
    ("受入テスト", "ユーザー側での受け入れテスト", 180),
    ("テスト", "各種テスト作業全般", 190),
    
    # 運用・保守工程
    ("リリース", "本番環境へのシステム展開", 200),
    ("デプロイ", "アプリケーションの配置・展開作業", 210),
    ("運用", "システムの運用・監視作業", 220),
    ("保守", "システムの保守・メンテナンス作業", 230),
    ("運用保守", "システムの運用と保守業務", 240),
    ("障害対応", "システム障害の対応・復旧作業", 250),
    ("不具合修正", "発見された不具合の修正作業", 260),
    ("バグ修正", "プログラムのバグを修正する作業", 270),
    
    # 管理・その他
    ("プロジェクト管理", "プロジェクト全体の管理・統括", 280),
    ("進捗管理", "プロジェクトの進捗を管理する業務", 290),
    ("品質管理", "システムの品質を管理する業務", 300),
    ("教育", "チームメンバーの教育・指導", 310),
    ("マネージメント", "チーム・プロジェクトの管理業務", 320),
    ("レビュー", "成果物のレビュー・査読作業", 330),
    ("調査", "技術調査・要件調査等の作業", 340),
    ("ドキュメント作成", "各種文書の作成作業", 350),
    ("資料作成", "プレゼン資料等の作成作業", 360),
    ("研修", "技術研修・教育研修の実施", 370),
]

def update_task_orders():
    """作業マスタの順序を更新"""
    try:
        with db_service.session_scope() as session:
            repo = Repository(session)
            
            print("作業マスタの順序更新を開始...")
            
            # 既存のタスクを取得
            existing_tasks = repo.get_master_by_kind('task')
            existing_task_names = {task.name for task in existing_tasks}
            
            print(f"既存作業数: {len(existing_tasks)}")
            
            # 新しいタスクを追加
            added_count = 0
            updated_count = 0
            
            for task_name, note, order_index in IT_DEVELOPMENT_TASKS:
                if task_name in existing_task_names:
                    # 既存タスクの順序を更新
                    for task in existing_tasks:
                        if task.name == task_name:
                            repo.update_master('task', task.id, task_name, note)
                            # 順序も更新
                            task.order_index = order_index
                            updated_count += 1
                            print(f"更新: {task_name} (順序: {order_index})")
                            break
                else:
                    # 新しいタスクを追加
                    repo.create_master('task', task_name, note)
                    # 作成後に順序を設定
                    new_task = session.query(repo.get_master_by_kind('task')[0].__class__).filter_by(name=task_name).first()
                    if new_task:
                        new_task.order_index = order_index
                    added_count += 1
                    print(f"追加: {task_name} (順序: {order_index})")
            
            # 順序が設定されていない既存タスクに大きな順序番号を設定
            for task in existing_tasks:
                if task.name not in [t[0] for t in IT_DEVELOPMENT_TASKS]:
                    if not hasattr(task, 'order_index') or task.order_index == 0:
                        task.order_index = 1000  # 最後尾に配置
                        updated_count += 1
                        print(f"既存タスクの順序設定: {task.name} (順序: 1000)")
            
            session.commit()
            
            print(f"\n作業マスタ更新完了:")
            print(f"- 新規追加: {added_count}件")
            print(f"- 更新: {updated_count}件")
            
            # 最終確認
            updated_tasks = repo.get_master_by_kind('task')
            print(f"- 総作業数: {len(updated_tasks)}件")
            
            print("\n現在の作業一覧（順序順）:")
            for i, task in enumerate(updated_tasks[:20], 1):  # 最初の20件のみ表示
                order = getattr(task, 'order_index', 0) if hasattr(task, 'order_index') else 0
                print(f"{i:2d}. {task.name} (順序: {order})")
            
            if len(updated_tasks) > 20:
                print(f"... (他 {len(updated_tasks) - 20} 件)")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_task_orders()