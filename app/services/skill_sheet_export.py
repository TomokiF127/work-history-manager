#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
スキルシート出力サービス
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from sqlalchemy.orm import Session

from services.repository import Repository
from services.stats import StatsService
from models import Project, TechUsage


class SkillSheetExportService:
    """スキルシートエクスポートサービス"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repo = Repository(session)
        self.stats_service = StatsService(session)
    
    def generate_skill_sheet_data(self, name: str = "氏名") -> Dict[str, Any]:
        """スキルシートデータを生成
        
        Args:
            name: 氏名
        
        Returns:
            スキルシートデータ
        """
        data = {
            "header": {
                "title": "職務経歴書",
                "date": datetime.now().strftime("%Y年%m月現在"),
                "name": name
            },
            "projects": self._generate_projects_data(),
            "technical_skills": self._generate_technical_skills_data(),
            "qualifications": [],  # TODO: 資格管理機能が必要
            "self_pr": ""  # TODO: 自己PR管理機能が必要
        }
        
        return data
    
    def _generate_projects_data(self) -> List[Dict[str, Any]]:
        """プロジェクトデータを生成（契約会社で合算）"""
        projects = self.repo.get_all_projects()
        
        # 契約会社ごとにグループ化
        company_groups = defaultdict(list)
        for project in projects:
            company = project.contract_company or "未設定"
            company_groups[company].append(project)
        
        result = []
        
        for company, company_projects in company_groups.items():
            # 契約会社内でプロジェクトを開始日順にソート
            company_projects.sort(key=lambda p: p.project_start or "9999-99-99")
            
            # 参画期間を計算（同じ契約会社の最初と最後）
            first_start = None
            last_end = None
            
            for project in company_projects:
                if project.project_start:
                    if not first_start or project.project_start < first_start:
                        first_start = project.project_start
                
                if project.project_end:
                    if not last_end or project.project_end > last_end:
                        last_end = project.project_end
                elif not last_end:
                    last_end = None  # 現在進行中
            
            # 各プロジェクトをエクスポート
            for project in company_projects:
                project_data = {
                    "participation_period": self._format_period_with_duration(first_start, last_end),
                    "project_period": self._format_period(project.project_start, project.project_end),
                    "project_name": project.name,
                    "business_content": project.work_summary,
                    "project_detail": project.detail,
                    "environment": self._get_project_environment(project.id),
                    "role": project.role.name if project.role else "",
                    "task": project.task.name if project.task else "",
                    "team_size": project.scale_text or "",
                    "contract_company": company,
                    "end_user": project.end_user or ""
                }
                result.append(project_data)
        
        # 開始日の新しい順にソート
        result.sort(key=lambda p: p.get("project_period", ""), reverse=True)
        
        return result
    
    def _get_project_environment(self, project_id: int) -> Dict[str, List[str]]:
        """プロジェクトの開発環境を取得"""
        environment = {
            "os": [],
            "language": [],
            "db": [],
            "framework": [],
            "tool": [],
            "cloud": []
        }
        
        # 各技術カテゴリの情報を取得
        for kind in ["os", "language", "framework", "tool", "cloud", "db"]:
            tech_ids = self.repo.get_project_techs(project_id, kind)
            techs = self.repo.get_master_by_kind(kind)
            
            for tech in techs:
                if tech.id in tech_ids:
                    if kind == "framework":
                        environment["framework"].append(tech.name)
                    else:
                        environment[kind].append(tech.name)
        
        return environment
    
    def _generate_technical_skills_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """技術スキルデータを生成"""
        skills_data = {}
        
        categories = [
            ('os', 'OS'),
            ('language', '言語'),
            ('db', 'DB'),
            ('framework', 'FW/ライブラリ'),
            ('tool', 'ツール'),
            ('cloud', 'クラウド')
        ]
        
        for kind, label in categories:
            stats = self.stats_service.get_all_tech_stats(kind)
            
            skills_data[label] = [
                {
                    "name": stat["name"],
                    "experience": stat["display"],
                    "months": stat["months"]
                }
                for stat in stats
            ]
        
        return skills_data
    
    def _format_period(self, start_date: Optional[str], end_date: Optional[str]) -> str:
        """期間をフォーマット"""
        if not start_date:
            return ""
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            start_str = f"{start.year}年{start.month}月"
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                end_str = f"{end.year}年{end.month}月"
                return f"{start_str}\n｜\n{end_str}"
            else:
                return f"{start_str}\n｜\n現在"
        except:
            return ""
    
    def _format_period_with_duration(self, start_date: Optional[str], end_date: Optional[str]) -> str:
        """期間と期間長をフォーマット"""
        period = self._format_period(start_date, end_date)
        
        if not period:
            return ""
        
        duration = self._calculate_duration(start_date, end_date)
        
        if duration:
            return f"{period}\n（{duration}）"
        
        return period
    
    def _calculate_duration(self, start_date: Optional[str], end_date: Optional[str]) -> str:
        """期間の長さを計算"""
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
    
    def export_to_docx(self, filepath: str, name: str = "氏名"):
        """DOCXファイルとしてエクスポート
        
        Args:
            filepath: 出力ファイルパス
            name: 氏名
        """
        data = self.generate_skill_sheet_data(name)
        doc = Document()
        
        # ヘッダー
        title = doc.add_heading(data["header"]["title"], level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 日付と氏名
        doc.add_paragraph(data["header"]["date"])
        doc.add_paragraph(f"氏名：{data['header']['name']}")
        
        # 開発経歴
        doc.add_heading("開発経歴", level=1)
        
        # プロジェクトテーブル
        if data["projects"]:
            table = doc.add_table(rows=1, cols=5)
            table.style = 'Table Grid'
            
            # ヘッダー行
            header_cells = table.rows[0].cells
            header_cells[0].text = "現場参画\n期間"
            header_cells[1].text = "プロジェクト\n期間"
            header_cells[2].text = "プロジェクト名および業務内容"
            header_cells[3].text = "開発環境"
            header_cells[4].text = "役割／担当／規模"
            
            # プロジェクトデータ
            for project in data["projects"]:
                row_cells = table.add_row().cells
                
                row_cells[0].text = project["participation_period"]
                row_cells[1].text = project["project_period"]
                
                # プロジェクト詳細
                project_text = f"【プロジェクト】\n{project['project_name']}\n\n"
                if project["business_content"]:
                    project_text += f"【業務内容】\n{project['business_content']}\n\n"
                if project["project_detail"]:
                    project_text += f"【プロジェクト詳細】\n{project['project_detail']}"
                row_cells[2].text = project_text
                
                # 開発環境
                env_text = ""
                if project["environment"]["os"]:
                    env_text += f"【OS】\n{', '.join(project['environment']['os'])}\n"
                if project["environment"]["language"]:
                    env_text += f"【言語】\n{', '.join(project['environment']['language'])}\n"
                if project["environment"]["db"]:
                    env_text += f"【DB】\n{', '.join(project['environment']['db'])}\n"
                if project["environment"]["framework"]:
                    env_text += f"【FW】\n{', '.join(project['environment']['framework'])}\n"
                if project["environment"]["tool"]:
                    env_text += f"【ツール】\n{', '.join(project['environment']['tool'][:5])}\n"  # 最初の5つのみ
                if project["environment"]["cloud"]:
                    env_text += f"【クラウド】\n{', '.join(project['environment']['cloud'])}\n"
                row_cells[3].text = env_text.strip()
                
                # 役割/規模
                role_text = ""
                if project["role"]:
                    role_text += f"【役割】\n{project['role']}\n"
                if project["task"]:
                    role_text += f"【担当】\n{project['task']}\n"
                if project["team_size"]:
                    role_text += f"【規模】\n{project['team_size']}"
                row_cells[4].text = role_text.strip()
        
        # テクニカルスキル
        doc.add_page_break()
        doc.add_heading("■　テクニカルスキル", level=1)
        
        if data["technical_skills"]:
            skill_table = doc.add_table(rows=1, cols=4)
            skill_table.style = 'Table Grid'
            
            # ヘッダー行は作らず、各カテゴリごとに行を追加
            skill_table.rows[0].cells[0].text = "カテゴリ"
            skill_table.rows[0].cells[1].text = "技術"
            skill_table.rows[0].cells[2].text = "経験期間"
            skill_table.rows[0].cells[3].text = "補足"
            
            for category, skills in data["technical_skills"].items():
                if skills:
                    # 技術名と期間を結合
                    tech_names = "\n".join([s["name"] for s in skills])
                    tech_experiences = "\n".join([s["experience"] for s in skills])
                    
                    row_cells = skill_table.add_row().cells
                    row_cells[0].text = category
                    row_cells[1].text = tech_names
                    row_cells[2].text = tech_experiences
                    row_cells[3].text = ""  # 補足は空欄
        
        # 保存
        doc.save(filepath)
    
    def export_to_markdown(self, filepath: str, name: str = "氏名"):
        """Markdownファイルとしてエクスポート
        
        Args:
            filepath: 出力ファイルパス
            name: 氏名
        """
        data = self.generate_skill_sheet_data(name)
        
        content = []
        content.append(f"# {data['header']['title']}")
        content.append("")
        content.append(data['header']['date'])
        content.append(f"氏名：{data['header']['name']}")
        content.append("")
        
        # 開発経歴
        content.append("## 開発経歴")
        content.append("")
        
        for project in data["projects"]:
            content.append(f"### {project['project_name']}")
            content.append("")
            period = project['project_period'].replace('\n', ' ')
            content.append(f"**期間**: {period}")
            content.append(f"**契約会社**: {project['contract_company']}")
            if project['end_user']:
                content.append(f"**エンドユーザー**: {project['end_user']}")
            content.append("")
            
            if project['business_content']:
                content.append("**業務内容**")
                content.append(project['business_content'])
                content.append("")
            
            if project['project_detail']:
                content.append("**詳細**")
                content.append(project['project_detail'])
                content.append("")
            
            content.append("**開発環境**")
            for key, label in [("os", "OS"), ("language", "言語"), ("db", "DB"), 
                              ("framework", "FW"), ("tool", "ツール"), ("cloud", "クラウド")]:
                if project['environment'][key]:
                    content.append(f"- {label}: {', '.join(project['environment'][key])}")
            content.append("")
            
            if project['role'] or project['task'] or project['team_size']:
                content.append("**体制**")
                if project['role']:
                    content.append(f"- 役割: {project['role']}")
                if project['task']:
                    content.append(f"- 担当: {project['task']}")
                if project['team_size']:
                    content.append(f"- 規模: {project['team_size']}")
                content.append("")
        
        # テクニカルスキル
        content.append("## テクニカルスキル")
        content.append("")
        
        for category, skills in data["technical_skills"].items():
            if skills:
                content.append(f"### {category}")
                content.append("")
                content.append("| 技術 | 経験期間 |")
                content.append("|------|----------|")
                for skill in skills:
                    content.append(f"| {skill['name']} | {skill['experience']} |")
                content.append("")
        
        # ファイルに書き込み
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))