#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
スキルシート出力テスト
"""

import sys
sys.path.append('app')

from services.db import db_service
from services.skill_sheet_export import SkillSheetExportService

def test_skill_sheet_export():
    """スキルシート出力のテスト"""
    try:
        with db_service.session_scope() as session:
            export_service = SkillSheetExportService(session)
            
            # テスト用ファイル名
            test_docx = "test_skill_sheet.docx"
            test_md = "test_skill_sheet.md"
            
            print("スキルシートを生成中...")
            
            # Word文書として出力
            export_service.export_to_docx(test_docx, "テスト太郎")
            print(f"Word文書を出力しました: {test_docx}")
            
            # Markdown文書として出力
            export_service.export_to_markdown(test_md, "テスト太郎")
            print(f"Markdown文書を出力しました: {test_md}")
            
            print("スキルシート出力テスト完了")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_skill_sheet_export()