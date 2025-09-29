#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
スキルシートテンプレート定義
"""

from typing import Dict, List, Any
from datetime import datetime

class SkillSheetTemplate:
    """スキルシートのテンプレート構造"""
    
    def __init__(self):
        self.sections = {
            "header": {
                "title": "職務経歴書",
                "date": None,  # 作成日（YYYY年MM月現在）
                "name": None   # 氏名
            },
            
            "development_history": {
                "title": "開発経歴",
                "period": None,  # 開始年月～現在
                "projects": []   # プロジェクトリスト
            },
            
            "other_history": {
                "title": "その他経歴（学習）", 
                "items": []  # 学習項目リスト
            },
            
            "qualifications": {
                "title": "■　取得資格等",
                "items": []  # 資格リスト
            },
            
            "technical_skills": {
                "title": "■　テクニカルスキル",
                "categories": {
                    "OS": [],
                    "言語": [],
                    "DB": [],
                    "FW/ライブラリ": [],
                    "ツール": [],
                    "クラウド": []
                }
            },
            
            "self_pr": {
                "title": "■　自己PR",
                "content": None,
                "subsections": []  # リーダー経験など
            }
        }
    
    def get_project_template(self) -> Dict[str, Any]:
        """プロジェクトテンプレート"""
        return {
            "participation_period": None,  # 現場参画期間（契約会社単位で合算）
            "project_period": None,        # プロジェクト期間
            "project_name": None,          # プロジェクト名
            "business_content": None,      # 業務内容
            "project_detail": None,        # プロジェクト詳細
            "environment": {               # 開発環境
                "os": [],
                "language": [],
                "db": [],
                "framework": [],
                "tool": [],
                "cloud": []
            },
            "role": None,                  # 役割
            "team_size": None,             # 規模
            "contract_company": None       # 契約会社
        }
    
    def get_skill_item_template(self) -> Dict[str, Any]:
        """技術スキル項目テンプレート"""
        return {
            "name": None,           # 技術名
            "experience": None,     # 経験期間（X年Yヶ月）
            "level": None          # スキルレベル（任意）
        }
    
    def format_period(self, start_date: str, end_date: str = None) -> str:
        """期間フォーマット
        
        Args:
            start_date: 開始日（YYYY-MM-DD）
            end_date: 終了日（YYYY-MM-DD）またはNone（現在まで）
        
        Returns:
            フォーマット済み期間文字列（例：2023年1月｜現在）
        """
        if not start_date:
            return ""
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            start_str = f"{start.year}年{start.month}月"
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                end_str = f"{end.year}年{end.month}月"
                return f"{start_str}｜{end_str}"
            else:
                return f"{start_str}｜現在"
        except:
            return ""
    
    def calculate_duration(self, start_date: str, end_date: str = None) -> str:
        """期間の長さを計算
        
        Args:
            start_date: 開始日（YYYY-MM-DD）
            end_date: 終了日（YYYY-MM-DD）またはNone（現在まで）
        
        Returns:
            期間文字列（例：1年10ヶ月）
        """
        if not start_date:
            return ""
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                end = datetime.now()
            
            # 月数を計算
            months = (end.year - start.year) * 12 + (end.month - start.month) + 1
            
            years = months // 12
            remaining_months = months % 12
            
            if years > 0 and remaining_months > 0:
                return f"{years}年{remaining_months}ヶ月"
            elif years > 0:
                return f"{years}年"
            else:
                return f"{remaining_months}ヶ月"
        except:
            return ""
    
    def format_skill_experience(self, months: int) -> str:
        """スキル経験期間のフォーマット
        
        Args:
            months: 経験月数
        
        Returns:
            フォーマット済み期間（例：1年10ヶ月）
        """
        if months <= 0:
            return "0ヶ月"
        
        years = months // 12
        remaining_months = months % 12
        
        if years > 0 and remaining_months > 0:
            return f"{years}年{remaining_months}ヶ月"
        elif years > 0:
            return f"{years}年"
        else:
            return f"{remaining_months}ヶ月"