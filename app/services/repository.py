from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date
from models import (
    Project, Engagement, TechUsage,
    OS, Language, Framework, Tool, Cloud, DB, Role, Task,
    ProjectOS, ProjectLanguage, ProjectFramework,
    ProjectTool, ProjectCloud, ProjectDB
)

class Repository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_all_projects(self) -> List[Project]:
        return self.session.query(Project).all()
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        return self.session.query(Project).filter_by(id=project_id).first()
    
    def create_project(self, data: Dict[str, Any]) -> Project:
        project = Project(**data)
        self.session.add(project)
        self.session.flush()
        return project
    
    def update_project(self, project_id: int, data: Dict[str, Any]) -> Optional[Project]:
        project = self.get_project_by_id(project_id)
        if project:
            for key, value in data.items():
                setattr(project, key, value)
            self.session.flush()
        return project
    
    def delete_project(self, project_id: int) -> bool:
        project = self.get_project_by_id(project_id)
        if project:
            self.session.delete(project)
            self.session.flush()
            return True
        return False
    
    def get_master_by_kind(self, kind: str) -> List:
        master_map = {
            'os': OS,
            'language': Language,
            'framework': Framework,
            'tool': Tool,
            'cloud': Cloud,
            'db': DB,
            'role': Role,
            'task': Task
        }
        model = master_map.get(kind)
        if model:
            return self.session.query(model).order_by(model.name).all()
        return []
    
    def create_master(self, kind: str, name: str, note: str = None) -> Optional[Any]:
        master_map = {
            'os': OS,
            'language': Language,
            'framework': Framework,
            'tool': Tool,
            'cloud': Cloud,
            'db': DB,
            'role': Role,
            'task': Task
        }
        model = master_map.get(kind)
        if model:
            instance = model(name=name, note=note)
            self.session.add(instance)
            self.session.flush()
            return instance
        return None
    
    def update_master(self, kind: str, master_id: int, name: str, note: str = None) -> bool:
        master_map = {
            'os': OS,
            'language': Language,
            'framework': Framework,
            'tool': Tool,
            'cloud': Cloud,
            'db': DB,
            'role': Role,
            'task': Task
        }
        model = master_map.get(kind)
        if model:
            instance = self.session.query(model).filter_by(id=master_id).first()
            if instance:
                instance.name = name
                instance.note = note
                self.session.flush()
                return True
        return False
    
    def delete_master(self, kind: str, master_id: int) -> bool:
        master_map = {
            'os': OS,
            'language': Language,
            'framework': Framework,
            'tool': Tool,
            'cloud': Cloud,
            'db': DB,
            'role': Role,
            'task': Task
        }
        model = master_map.get(kind)
        if model:
            instance = self.session.query(model).filter_by(id=master_id).first()
            if instance:
                self.session.delete(instance)
                self.session.flush()
                return True
        return False
    
    def get_engagements_by_project(self, project_id: int) -> List[Engagement]:
        return self.session.query(Engagement).filter_by(project_id=project_id).order_by(Engagement.site_start).all()
    
    def create_engagement(self, data: Dict[str, Any]) -> Engagement:
        engagement = Engagement(**data)
        self.session.add(engagement)
        self.session.flush()
        return engagement
    
    def update_engagement(self, engagement_id: int, data: Dict[str, Any]) -> Optional[Engagement]:
        engagement = self.session.query(Engagement).filter_by(id=engagement_id).first()
        if engagement:
            for key, value in data.items():
                setattr(engagement, key, value)
            self.session.flush()
        return engagement
    
    def delete_engagement(self, engagement_id: int) -> bool:
        engagement = self.session.query(Engagement).filter_by(id=engagement_id).first()
        if engagement:
            self.session.delete(engagement)
            self.session.flush()
            return True
        return False
    
    def get_tech_usages_by_project(self, project_id: int) -> List[TechUsage]:
        return self.session.query(TechUsage).filter_by(project_id=project_id).all()
    
    def create_tech_usage(self, data: Dict[str, Any]) -> TechUsage:
        usage = TechUsage(**data)
        self.session.add(usage)
        self.session.flush()
        return usage
    
    def update_tech_usage(self, usage_id: int, data: Dict[str, Any]) -> Optional[TechUsage]:
        usage = self.session.query(TechUsage).filter_by(id=usage_id).first()
        if usage:
            for key, value in data.items():
                setattr(usage, key, value)
            self.session.flush()
        return usage
    
    def delete_tech_usage(self, usage_id: int) -> bool:
        usage = self.session.query(TechUsage).filter_by(id=usage_id).first()
        if usage:
            self.session.delete(usage)
            self.session.flush()
            return True
        return False
    
    def link_project_tech(self, project_id: int, kind: str, tech_ids: List[int]):
        relation_map = {
            'os': (ProjectOS, 'os_id'),
            'language': (ProjectLanguage, 'language_id'),
            'framework': (ProjectFramework, 'framework_id'),
            'tool': (ProjectTool, 'tool_id'),
            'cloud': (ProjectCloud, 'cloud_id'),
            'db': (ProjectDB, 'db_id')
        }
        
        if kind not in relation_map:
            return
        
        model, tech_field = relation_map[kind]
        
        existing = self.session.query(model).filter_by(project_id=project_id).all()
        for item in existing:
            self.session.delete(item)
        
        for tech_id in tech_ids:
            relation = model(project_id=project_id, **{tech_field: tech_id})
            self.session.add(relation)
        
        self.session.flush()
    
    def get_project_techs(self, project_id: int, kind: str) -> List[int]:
        relation_map = {
            'os': (ProjectOS, 'os_id'),
            'language': (ProjectLanguage, 'language_id'),
            'framework': (ProjectFramework, 'framework_id'),
            'tool': (ProjectTool, 'tool_id'),
            'cloud': (ProjectCloud, 'cloud_id'),
            'db': (ProjectDB, 'db_id')
        }
        
        if kind not in relation_map:
            return []
        
        model, tech_field = relation_map[kind]
        results = self.session.query(model).filter_by(project_id=project_id).all()
        return [getattr(r, tech_field) for r in results]
    
    def auto_generate_tech_usages_from_project(self, project_id: int):
        project = self.get_project_by_id(project_id)
        if not project:
            return
        
        existing_usages = self.get_tech_usages_by_project(project_id)
        existing_keys = {(u.kind, u.tech_id) for u in existing_usages}
        
        tech_kinds = ['os', 'language', 'framework', 'tool', 'cloud', 'db']
        
        for kind in tech_kinds:
            tech_ids = self.get_project_techs(project_id, kind)
            for tech_id in tech_ids:
                if (kind, tech_id) not in existing_keys:
                    usage = TechUsage(
                        project_id=project_id,
                        kind=kind,
                        tech_id=tech_id,
                        start=project.project_start,
                        end=project.project_end
                    )
                    self.session.add(usage)
        
        self.session.flush()
    
    def auto_generate_tech_usages_from_engagement(self, project_id: int, engagement_id: int):
        engagement = self.session.query(Engagement).filter_by(id=engagement_id).first()
        if not engagement:
            return
        
        existing_usages = self.get_tech_usages_by_project(project_id)
        existing_keys = {(u.kind, u.tech_id) for u in existing_usages}
        
        tech_kinds = ['os', 'language', 'framework', 'tool', 'cloud', 'db']
        
        for kind in tech_kinds:
            tech_ids = self.get_project_techs(project_id, kind)
            for tech_id in tech_ids:
                if (kind, tech_id) not in existing_keys:
                    usage = TechUsage(
                        project_id=project_id,
                        kind=kind,
                        tech_id=tech_id,
                        start=engagement.site_start,
                        end=engagement.site_end
                    )
                    self.session.add(usage)
        
        self.session.flush()
    
    def filter_projects(self, filters: Dict[str, Any]) -> List[Project]:
        query = self.session.query(Project)
        
        if 'start_date' in filters and filters['start_date']:
            query = query.filter(or_(
                Project.project_end == None,
                Project.project_end >= filters['start_date']
            ))
        
        if 'end_date' in filters and filters['end_date']:
            query = query.filter(Project.project_start <= filters['end_date'])
        
        if 'role_id' in filters and filters['role_id']:
            query = query.filter(Project.role_id == filters['role_id'])
        
        if 'text' in filters and filters['text']:
            text = f"%{filters['text']}%"
            query = query.filter(or_(
                Project.name.like(text),
                Project.work_summary.like(text),
                Project.detail.like(text)
            ))
        
        if 'tech_filters' in filters:
            for kind, tech_ids in filters['tech_filters'].items():
                if tech_ids:
                    relation_map = {
                        'os': ProjectOS,
                        'language': ProjectLanguage,
                        'framework': ProjectFramework,
                        'tool': ProjectTool,
                        'cloud': ProjectCloud,
                        'db': ProjectDB
                    }
                    
                    if kind in relation_map:
                        model = relation_map[kind]
                        tech_field = f"{kind}_id" if kind != 'db' else 'db_id'
                        subq = self.session.query(model.project_id).filter(
                            getattr(model, tech_field).in_(tech_ids)
                        ).subquery()
                        query = query.filter(Project.id.in_(subq))
        
        return query.order_by(Project.project_start.desc()).all()
    
    def delete_tech_usages_by_project(self, project_id: int):
        """指定プロジェクトの技術使用期間をすべて削除"""
        self.session.query(TechUsage).filter(
            TechUsage.project_id == project_id
        ).delete()
        self.session.commit()
    
    def create_tech_usage(self, data: dict):
        """技術使用期間を作成"""
        tech_usage = TechUsage(**data)
        self.session.add(tech_usage)
        self.session.commit()
        return tech_usage