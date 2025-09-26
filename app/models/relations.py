from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base

class ProjectOS(Base):
    __tablename__ = "project_oses"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    os_id = Column(Integer, ForeignKey("oses.id"), primary_key=True)
    
    project = relationship("Project", back_populates="project_oses")
    os = relationship("OS", back_populates="projects")
    
    __table_args__ = (UniqueConstraint('project_id', 'os_id'),)

class ProjectLanguage(Base):
    __tablename__ = "project_languages"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    language_id = Column(Integer, ForeignKey("languages.id"), primary_key=True)
    
    project = relationship("Project", back_populates="project_languages")
    language = relationship("Language", back_populates="projects")
    
    __table_args__ = (UniqueConstraint('project_id', 'language_id'),)

class ProjectFramework(Base):
    __tablename__ = "project_frameworks"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    framework_id = Column(Integer, ForeignKey("frameworks.id"), primary_key=True)
    
    project = relationship("Project", back_populates="project_frameworks")
    framework = relationship("Framework", back_populates="projects")
    
    __table_args__ = (UniqueConstraint('project_id', 'framework_id'),)

class ProjectTool(Base):
    __tablename__ = "project_tools"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    tool_id = Column(Integer, ForeignKey("tools.id"), primary_key=True)
    
    project = relationship("Project", back_populates="project_tools")
    tool = relationship("Tool", back_populates="projects")
    
    __table_args__ = (UniqueConstraint('project_id', 'tool_id'),)

class ProjectCloud(Base):
    __tablename__ = "project_clouds"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    cloud_id = Column(Integer, ForeignKey("clouds.id"), primary_key=True)
    
    project = relationship("Project", back_populates="project_clouds")
    cloud = relationship("Cloud", back_populates="projects")
    
    __table_args__ = (UniqueConstraint('project_id', 'cloud_id'),)

class ProjectDB(Base):
    __tablename__ = "project_dbs"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    db_id = Column(Integer, ForeignKey("dbs.id"), primary_key=True)
    
    project = relationship("Project", back_populates="project_dbs")
    db = relationship("DB", back_populates="projects")
    
    __table_args__ = (UniqueConstraint('project_id', 'db_id'),)