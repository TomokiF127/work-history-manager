import csv
import os
from typing import Optional
from sqlalchemy.orm import Session
from services.stats import StatsService

class ExportService:
    def __init__(self, session: Session):
        self.session = session
        self.stats = StatsService(session)
    
    def export_category_csv(
        self, 
        kind: str, 
        file_path: str,
        start_filter: Optional[str] = None,
        end_filter: Optional[str] = None
    ) -> bool:
        """
        カテゴリー別の統計をCSVファイルにエクスポート
        """
        try:
            stats_data = self.stats.get_all_tech_stats(kind, start_filter, end_filter)
            
            from config import config
            encoding = config.get_csv_encoding()
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.writer(f)
                writer.writerow(['技術名', '月数', '年月'])
                
                for item in stats_data:
                    writer.writerow([
                        item['name'],
                        item['months'],
                        item['display']
                    ])
            
            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False
    
    def export_category_md(
        self, 
        kind: str, 
        file_path: str,
        start_filter: Optional[str] = None,
        end_filter: Optional[str] = None
    ) -> bool:
        """
        カテゴリー別の統計をMarkdownファイルにエクスポート
        """
        try:
            stats_data = self.stats.get_all_tech_stats(kind, start_filter, end_filter)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            kind_display_map = {
                'os': 'OS',
                'language': '言語',
                'framework': 'フレームワーク',
                'tool': 'ツール',
                'cloud': 'クラウド',
                'db': 'データベース'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {kind_display_map.get(kind, kind)}経験\n\n")
                
                if start_filter or end_filter:
                    f.write("## 集計期間\n")
                    if start_filter:
                        f.write(f"- 開始: {start_filter}\n")
                    if end_filter:
                        f.write(f"- 終了: {end_filter}\n")
                    f.write("\n")
                
                f.write("| 技術名 | 月数 | 年月 |\n")
                f.write("|--------|------|------|\n")
                
                for item in stats_data:
                    f.write(f"| {item['name']} | {item['months']} | {item['display']} |\n")
                
                f.write(f"\n合計: {len(stats_data)}件\n")
            
            return True
        except Exception as e:
            print(f"Markdown export error: {e}")
            return False
    
    def export_all_categories_csv(
        self, 
        directory: str,
        start_filter: Optional[str] = None,
        end_filter: Optional[str] = None
    ) -> dict:
        """
        全カテゴリーのCSVを一括エクスポート
        """
        categories = ['os', 'language', 'framework', 'tool', 'cloud', 'db']
        results = {}
        
        for category in categories:
            file_name = f"{category}.csv"
            file_path = os.path.join(directory, file_name)
            success = self.export_category_csv(
                category, file_path, start_filter, end_filter
            )
            results[category] = success
        
        return results
    
    def export_all_categories_md(
        self, 
        directory: str,
        start_filter: Optional[str] = None,
        end_filter: Optional[str] = None
    ) -> dict:
        """
        全カテゴリーのMarkdownを一括エクスポート
        """
        categories = ['os', 'language', 'framework', 'tool', 'cloud', 'db']
        results = {}
        
        for category in categories:
            file_name = f"{category}.md"
            file_path = os.path.join(directory, file_name)
            success = self.export_category_md(
                category, file_path, start_filter, end_filter
            )
            results[category] = success
        
        return results
    
    def export_projects_csv(
        self,
        file_path: str,
        start_filter: Optional[str] = None,
        end_filter: Optional[str] = None
    ) -> bool:
        """
        プロジェクト一覧をCSVにエクスポート
        """
        try:
            from services.repository import Repository
            repo = Repository(self.session)
            
            filters = {}
            if start_filter:
                filters['start_date'] = start_filter
            if end_filter:
                filters['end_date'] = end_filter
            
            projects = repo.filter_projects(filters)
            
            from config import config
            encoding = config.get_csv_encoding()
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.writer(f)
                writer.writerow([
                    'プロジェクト名', '業務内容', '開始', '終了',
                    '役割', '作業', '規模'
                ])
                
                for project in projects:
                    role_name = project.role.name if project.role else ''
                    task_name = project.task.name if project.task else ''
                    
                    writer.writerow([
                        project.name,
                        project.work_summary or '',
                        project.project_start or '',
                        project.project_end or '継続中',
                        role_name,
                        task_name,
                        project.scale_text or ''
                    ])
            
            return True
        except Exception as e:
            print(f"Projects CSV export error: {e}")
            return False