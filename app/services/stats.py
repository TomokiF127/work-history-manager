from typing import List, Tuple, Optional, Set, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from models import Project, TechUsage, Engagement
from services.repository import Repository

class StatsService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = Repository(session)
    
    def month_range_inclusive(self, start_str: Optional[str], end_str: Optional[str]) -> List[Tuple[int, int]]:
        """
        期間から月単位のリストを生成（両端含む）
        """
        if not start_str:
            return []
        
        start = datetime.strptime(start_str, "%Y-%m-%d").date()
        
        if end_str:
            end = datetime.strptime(end_str, "%Y-%m-%d").date()
        else:
            end = date.today()
        
        months = []
        current = date(start.year, start.month, 1)
        end_month = date(end.year, end.month, 1)
        
        while current <= end_month:
            months.append((current.year, current.month))
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
        
        return months
    
    def union_months(self, ranges: List[List[Tuple[int, int]]]) -> Set[Tuple[int, int]]:
        """
        複数の月リストの和集合を取得（重複排除）
        """
        result = set()
        for range_list in ranges:
            result.update(range_list)
        return result
    
    def tech_experience_unique_months(
        self, 
        kind: str, 
        tech_id: int,
        start_filter: Optional[str] = None,
        end_filter: Optional[str] = None
    ) -> int:
        """
        特定技術の経験月数を計算（重複なしカウント）
        
        # 将来の拡張ポイント：
        # 設定により重複許容（ダブルカウント）モードに切り替える場合は
        # union_months() を使わずに各期間の月数を単純合計する実装に変更
        """
        usages = self.session.query(TechUsage).filter(
            TechUsage.kind == kind,
            TechUsage.tech_id == tech_id
        ).all()
        
        if not usages:
            return 0
        
        all_ranges = []
        
        for usage in usages:
            project = self.session.query(Project).filter_by(id=usage.project_id).first()
            if not project:
                continue
            
            if usage.start and usage.end:
                use_start = usage.start
                use_end = usage.end
            elif usage.start:
                use_start = usage.start
                use_end = None
            else:
                use_start = project.project_start
                use_end = project.project_end
            
            if not use_start:
                continue
            
            if start_filter:
                if use_end and use_end < start_filter:
                    continue
                if use_start < start_filter:
                    use_start = start_filter
            
            if end_filter:
                if use_start > end_filter:
                    continue
                if not use_end or use_end > end_filter:
                    use_end = end_filter
            
            month_range = self.month_range_inclusive(use_start, use_end)
            all_ranges.append(month_range)
        
        unique_months = self.union_months(all_ranges)
        return len(unique_months)
    
    def get_all_tech_stats(
        self, 
        kind: str,
        start_filter: Optional[str] = None,
        end_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        指定カテゴリの全技術の統計を取得
        """
        techs = self.repo.get_master_by_kind(kind)
        stats = []
        
        for tech in techs:
            months = self.tech_experience_unique_months(
                kind, tech.id, start_filter, end_filter
            )
            
            if months > 0:
                years = months // 12
                remaining_months = months % 12
                
                if years > 0 and remaining_months > 0:
                    display = f"{years}年{remaining_months}ヶ月"
                elif years > 0:
                    display = f"{years}年"
                else:
                    display = f"{remaining_months}ヶ月"
                
                stats.append({
                    'id': tech.id,
                    'name': tech.name,
                    'months': months,
                    'display': display
                })
        
        stats.sort(key=lambda x: x['months'], reverse=True)
        return stats
    
    def get_project_period_stats(self, project_id: int) -> Dict[str, Any]:
        """
        プロジェクトの期間統計を取得
        """
        project = self.repo.get_project_by_id(project_id)
        if not project:
            return {}
        
        if project.project_start:
            months = self.month_range_inclusive(
                project.project_start, 
                project.project_end
            )
            month_count = len(months)
        else:
            month_count = 0
        
        engagements = self.repo.get_engagements_by_project(project_id)
        engagement_months = 0
        
        for engagement in engagements:
            if engagement.site_start:
                e_months = self.month_range_inclusive(
                    engagement.site_start,
                    engagement.site_end
                )
                engagement_months += len(e_months)
        
        return {
            'project_months': month_count,
            'engagement_months': engagement_months,
            'engagement_count': len(engagements)
        }
    
    def get_summary_stats(
        self,
        start_filter: Optional[str] = None,
        end_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        全体のサマリー統計を取得
        """
        projects = self.repo.filter_projects({
            'start_date': start_filter,
            'end_date': end_filter
        })
        
        total_projects = len(projects)
        
        categories = ['os', 'language', 'framework', 'tool', 'cloud', 'db']
        tech_counts = {}
        
        for category in categories:
            stats = self.get_all_tech_stats(category, start_filter, end_filter)
            tech_counts[category] = len(stats)
        
        all_months = []
        for project in projects:
            if project.project_start:
                months = self.month_range_inclusive(
                    project.project_start,
                    project.project_end
                )
                all_months.append(months)
        
        unique_project_months = len(self.union_months(all_months))
        
        return {
            'total_projects': total_projects,
            'total_months': unique_project_months,
            'tech_counts': tech_counts
        }