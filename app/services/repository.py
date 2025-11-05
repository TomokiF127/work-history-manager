from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date
from models import (
    Project, Engagement, TechUsage, SelfPR,
    OS, Language, Framework, Tool, Cloud, DB, Role, Task,
    ProjectOS, ProjectLanguage, ProjectFramework,
    ProjectTool, ProjectCloud, ProjectDB,
    ProjectRole, ProjectTask, ProficiencyLevel
)
from models.master import Qualification
from models.qualification import UserQualification
from models.other_experience import OtherExperience

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
            'qualification': Qualification,
            'role': Role,
            'task': Task,
            'proficiency': ProficiencyLevel
        }
        model = master_map.get(kind)
        if model:
            # 役割と作業と習熟度は順序で並び替え、その他は名前で並び替え
            if kind in ['role', 'task', 'proficiency']:
                return self.session.query(model).order_by(model.order_index, model.name).all()
            else:
                return self.session.query(model).order_by(model.name).all()
        return []
    
    def create_master(self, kind: str, name: str, note: str = None, proficiency_id: int = None) -> Optional[Any]:
        master_map = {
            'os': OS,
            'language': Language,
            'framework': Framework,
            'tool': Tool,
            'cloud': Cloud,
            'db': DB,
            'qualification': Qualification,
            'role': Role,
            'task': Task,
            'proficiency': ProficiencyLevel
        }
        model = master_map.get(kind)
        if model:
            # 役割と作業と習熟度の場合はorder_indexを自動設定
            if kind in ['role', 'task', 'proficiency']:
                # 最大のorder_indexを取得
                max_order = self.session.query(model).count()
                instance = model(name=name, note=note, order_index=max_order)
            else:
                # 技術マスタの場合は習熟度も設定
                if kind in ['os', 'language', 'framework', 'tool', 'cloud', 'db']:
                    instance = model(name=name, note=note, proficiency_id=proficiency_id)
                else:
                    instance = model(name=name, note=note)
            self.session.add(instance)
            self.session.flush()
            return instance
        return None
    
    def update_master(self, kind: str, master_id: int, name: str, note: str = None, proficiency_id: int = None) -> bool:
        master_map = {
            'os': OS,
            'language': Language,
            'framework': Framework,
            'tool': Tool,
            'cloud': Cloud,
            'db': DB,
            'qualification': Qualification,
            'role': Role,
            'task': Task,
            'proficiency': ProficiencyLevel
        }
        model = master_map.get(kind)
        if model:
            instance = self.session.query(model).filter_by(id=master_id).first()
            if instance:
                instance.name = name
                instance.note = note
                # 技術マスタの場合は習熟度も更新
                if kind in ['os', 'language', 'framework', 'tool', 'cloud', 'db']:
                    instance.proficiency_id = proficiency_id
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
            'qualification': Qualification,
            'role': Role,
            'task': Task,
            'proficiency': ProficiencyLevel
        }
        model = master_map.get(kind)
        if model:
            instance = self.session.query(model).filter_by(id=master_id).first()
            if instance:
                self.session.delete(instance)
                self.session.flush()
                return True
        return False

    def normalize_master_order(self, kind: str):
        """マスタのorder_indexを0から連番に正規化"""
        if kind not in ['role', 'task', 'proficiency']:
            return

        model_map = {
            'role': Role,
            'task': Task,
            'proficiency': ProficiencyLevel
        }
        model = model_map.get(kind)
        if not model:
            return

        # 現在のorder_indexでソートして取得
        items = self.session.query(model).order_by(model.order_index, model.id).all()

        # 0から連番に振り直す
        for index, item in enumerate(items):
            item.order_index = index

        self.session.flush()

    def move_master_up(self, kind: str, master_id: int) -> bool:
        """マスタを1つ上に移動（order_indexを小さくする）"""
        if kind not in ['role', 'task', 'proficiency']:
            return False

        # 順序を正規化
        self.normalize_master_order(kind)

        model_map = {
            'role': Role,
            'task': Task,
            'proficiency': ProficiencyLevel
        }
        model = model_map.get(kind)
        if not model:
            return False

        # 対象アイテムを取得
        target = self.session.query(model).filter_by(id=master_id).first()
        if not target:
            return False

        # すでに一番上の場合
        if target.order_index == 0:
            return False

        # 1つ上のアイテムを取得
        prev_item = self.session.query(model).filter(
            model.order_index == target.order_index - 1
        ).first()

        if prev_item:
            # order_indexを入れ替え
            target.order_index, prev_item.order_index = prev_item.order_index, target.order_index
            self.session.flush()
            return True

        return False

    def move_master_down(self, kind: str, master_id: int) -> bool:
        """マスタを1つ下に移動（order_indexを大きくする）"""
        if kind not in ['role', 'task', 'proficiency']:
            return False

        # 順序を正規化
        self.normalize_master_order(kind)

        model_map = {
            'role': Role,
            'task': Task,
            'proficiency': ProficiencyLevel
        }
        model = model_map.get(kind)
        if not model:
            return False

        # 対象アイテムを取得
        target = self.session.query(model).filter_by(id=master_id).first()
        if not target:
            return False

        # 最大のorder_indexを取得
        max_order = self.session.query(model).count() - 1

        # すでに一番下の場合
        if target.order_index >= max_order:
            return False

        # 1つ下のアイテムを取得
        next_item = self.session.query(model).filter(
            model.order_index == target.order_index + 1
        ).first()

        if next_item:
            # order_indexを入れ替え
            target.order_index, next_item.order_index = next_item.order_index, target.order_index
            self.session.flush()
            return True

        return False

    def update_tech_proficiency(self, kind: str, tech_id: int, proficiency_id: Optional[int]) -> bool:
        """技術の習熟度を更新"""
        tech_map = {
            'os': OS,
            'language': Language,
            'framework': Framework,
            'tool': Tool,
            'cloud': Cloud,
            'db': DB
        }
        model = tech_map.get(kind)
        if model:
            tech = self.session.query(model).filter_by(id=tech_id).first()
            if tech:
                tech.proficiency_id = proficiency_id
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

    def link_project_roles(self, project_id: int, role_ids: List[int]):
        """プロジェクトに役割を複数関連付ける"""
        # 既存の関連を削除
        self.session.query(ProjectRole).filter_by(project_id=project_id).delete()

        # 新しい関連を追加
        for role_id in role_ids:
            relation = ProjectRole(project_id=project_id, role_id=role_id)
            self.session.add(relation)

        self.session.flush()

    def get_project_roles(self, project_id: int) -> List[int]:
        """プロジェクトに関連付けられた役割IDのリストを取得"""
        results = self.session.query(ProjectRole).filter_by(project_id=project_id).all()
        return [r.role_id for r in results]

    def link_project_tasks(self, project_id: int, task_ids: List[int]):
        """プロジェクトに作業を複数関連付ける"""
        # 既存の関連を削除
        self.session.query(ProjectTask).filter_by(project_id=project_id).delete()

        # 新しい関連を追加
        for task_id in task_ids:
            relation = ProjectTask(project_id=project_id, task_id=task_id)
            self.session.add(relation)

        self.session.flush()

    def get_project_tasks(self, project_id: int) -> List[int]:
        """プロジェクトに関連付けられた作業IDのリストを取得"""
        results = self.session.query(ProjectTask).filter_by(project_id=project_id).all()
        return [r.task_id for r in results]
    
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
    
    # 自己PR管理
    def get_all_self_prs(self) -> List[SelfPR]:
        """全ての自己PRを取得（順序順）"""
        return self.session.query(SelfPR).filter_by(is_active=True).order_by(SelfPR.order_index).all()
    
    def get_self_pr_by_id(self, pr_id: int) -> Optional[SelfPR]:
        """IDで自己PRを取得"""
        return self.session.query(SelfPR).filter_by(id=pr_id).first()
    
    def create_self_pr(self, data: Dict[str, Any]) -> SelfPR:
        """自己PRを作成"""
        pr = SelfPR(**data)
        self.session.add(pr)
        self.session.flush()
        return pr
    
    def update_self_pr(self, pr_id: int, data: Dict[str, Any]) -> Optional[SelfPR]:
        """自己PRを更新"""
        pr = self.get_self_pr_by_id(pr_id)
        if pr:
            for key, value in data.items():
                setattr(pr, key, value)
            self.session.flush()
        return pr
    
    def delete_self_pr(self, pr_id: int) -> bool:
        """自己PRを削除"""
        pr = self.get_self_pr_by_id(pr_id)
        if pr:
            self.session.delete(pr)
            self.session.flush()
            return True
        return False
    
    def reorder_self_prs(self, pr_orders: List[Dict[str, int]]):
        """自己PRの順序を変更"""
        for item in pr_orders:
            pr = self.get_self_pr_by_id(item['id'])
            if pr:
                pr.order_index = item['order']
        self.session.flush()
    
    # 資格取得年月の管理
    def get_all_user_qualifications(self) -> List[UserQualification]:
        """全ての取得資格を取得"""
        return self.session.query(UserQualification).join(Qualification).order_by(UserQualification.obtained_date.desc()).all()
    
    def get_user_qualification_by_id(self, qualification_id: int) -> Optional[UserQualification]:
        """IDで取得資格を取得"""
        return self.session.query(UserQualification).filter_by(id=qualification_id).first()
    
    def create_user_qualification(self, data: Dict[str, Any]) -> UserQualification:
        """取得資格を作成"""
        qualification = UserQualification(**data)
        self.session.add(qualification)
        self.session.flush()
        return qualification
    
    def update_user_qualification(self, qualification_id: int, data: Dict[str, Any]) -> Optional[UserQualification]:
        """取得資格を更新"""
        qualification = self.get_user_qualification_by_id(qualification_id)
        if qualification:
            for key, value in data.items():
                setattr(qualification, key, value)
            self.session.flush()
        return qualification
    
    def delete_user_qualification(self, qualification_id: int) -> bool:
        """取得資格を削除"""
        qualification = self.get_user_qualification_by_id(qualification_id)
        if qualification:
            self.session.delete(qualification)
            self.session.flush()
            return True
        return False
    
    # その他経歴の管理
    def get_all_other_experiences(self) -> List[OtherExperience]:
        """全てのその他経歴を取得"""
        return self.session.query(OtherExperience).filter_by(is_active=1).order_by(OtherExperience.order_index).all()
    
    def get_other_experience_by_id(self, experience_id: int) -> Optional[OtherExperience]:
        """IDでその他経歴を取得"""
        return self.session.query(OtherExperience).filter_by(id=experience_id).first()
    
    def create_other_experience(self, data: Dict[str, Any]) -> OtherExperience:
        """その他経歴を作成"""
        experience = OtherExperience(**data)
        self.session.add(experience)
        self.session.flush()
        return experience
    
    def update_other_experience(self, experience_id: int, data: Dict[str, Any]) -> Optional[OtherExperience]:
        """その他経歴を更新"""
        experience = self.get_other_experience_by_id(experience_id)
        if experience:
            for key, value in data.items():
                setattr(experience, key, value)
            self.session.flush()
        return experience
    
    def delete_other_experience(self, experience_id: int) -> bool:
        """その他経歴を削除"""
        experience = self.get_other_experience_by_id(experience_id)
        if experience:
            experience.is_active = 0
            self.session.flush()
            return True
        return False
    
    def reorder_other_experiences(self, experience_orders: List[Dict[str, int]]):
        """その他経歴の順序を変更"""
        for item in experience_orders:
            experience = self.get_other_experience_by_id(item['id'])
            if experience:
                experience.order_index = item['order']
        self.session.flush()