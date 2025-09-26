from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    work_summary = Column(Text)
    detail = Column(Text)
    project_start = Column(Text)
    project_end = Column(Text)
    role_id = Column(Integer, ForeignKey("roles.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    scale_text = Column(Text)
    
    role = relationship("Role", back_populates="projects")
    task = relationship("Task", back_populates="projects")
    engagements = relationship("Engagement", back_populates="project", cascade="all, delete-orphan")
    tech_usages = relationship("TechUsage", back_populates="project", cascade="all, delete-orphan")
    
    project_oses = relationship("ProjectOS", back_populates="project", cascade="all, delete-orphan")
    project_languages = relationship("ProjectLanguage", back_populates="project", cascade="all, delete-orphan")
    project_frameworks = relationship("ProjectFramework", back_populates="project", cascade="all, delete-orphan")
    project_tools = relationship("ProjectTool", back_populates="project", cascade="all, delete-orphan")
    project_clouds = relationship("ProjectCloud", back_populates="project", cascade="all, delete-orphan")
    project_dbs = relationship("ProjectDB", back_populates="project", cascade="all, delete-orphan")