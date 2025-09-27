from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base

class ProjectRole(Base):
    __tablename__ = "project_roles"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    
    project = relationship("Project", back_populates="project_roles")
    role = relationship("Role", back_populates="project_roles")
    
    __table_args__ = (UniqueConstraint('project_id', 'role_id'),)

class ProjectTask(Base):
    __tablename__ = "project_tasks"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    
    project = relationship("Project", back_populates="project_tasks")
    task = relationship("Task", back_populates="project_tasks")
    
    __table_args__ = (UniqueConstraint('project_id', 'task_id'),)