#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
既存のプロジェクトの役割・作業データを新形式に移行するスクリプト
"""

import sys
from pathlib import Path

# アプリケーションのパスを追加
app_path = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_path))

from services.db import db_service
from services.repository import Repository
from models import Project

def migrate_roles_tasks():
    """既存のrole_id/task_idをproject_roles/project_tasksテーブルに移行"""

    with db_service.session_scope() as session:
        repo = Repository(session)

        # 全プロジェクトを取得
        projects = repo.get_all_projects()

        migrated_count = 0
        for project in projects:
            # 役割の移行
            if project.role_id:
                # 既にproject_rolesにデータがあるか確認
                existing_roles = repo.get_project_roles(project.id)
                if not existing_roles:
                    # 古い形式のrole_idを新形式に移行
                    repo.link_project_roles(project.id, [project.role_id])
                    print(f"プロジェクト '{project.name}' の役割を移行: {project.role_id}")
                    migrated_count += 1

            # 作業の移行
            if project.task_id:
                # 既にproject_tasksにデータがあるか確認
                existing_tasks = repo.get_project_tasks(project.id)
                if not existing_tasks:
                    # 古い形式のtask_idを新形式に移行
                    repo.link_project_tasks(project.id, [project.task_id])
                    print(f"プロジェクト '{project.name}' の作業を移行: {project.task_id}")
                    migrated_count += 1

        print(f"\n移行完了: {migrated_count}件のプロジェクトを処理しました")
        print("注意: projects.role_id と projects.task_id は互換性のために残されています")

if __name__ == '__main__':
    print("=== 役割・作業データ移行スクリプト ===")
    print("既存のプロジェクトデータを新しい複数選択形式に移行します\n")

    response = input("移行を実行しますか？ (yes/no): ")
    if response.lower() in ['yes', 'y']:
        migrate_roles_tasks()
    else:
        print("移行をキャンセルしました")
