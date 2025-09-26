from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from models.base import Base

class OS(Base):
    __tablename__ = "oses"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    
    projects = relationship("ProjectOS", back_populates="os")

class Language(Base):
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    
    projects = relationship("ProjectLanguage", back_populates="language")

class Framework(Base):
    __tablename__ = "frameworks"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    
    projects = relationship("ProjectFramework", back_populates="framework")

class Tool(Base):
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    
    projects = relationship("ProjectTool", back_populates="tool")

class Cloud(Base):
    __tablename__ = "clouds"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    
    projects = relationship("ProjectCloud", back_populates="cloud")

class DB(Base):
    __tablename__ = "dbs"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    
    projects = relationship("ProjectDB", back_populates="db")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    
    projects = relationship("Project", back_populates="role")
    engagements = relationship("Engagement", back_populates="role_override")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    
    projects = relationship("Project", back_populates="task")
    engagements = relationship("Engagement", back_populates="task_override")