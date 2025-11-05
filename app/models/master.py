from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class OS(Base):
    __tablename__ = "oses"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    proficiency_id = Column(Integer, ForeignKey("proficiency_levels.id"))  # 習熟度

    projects = relationship("ProjectOS", back_populates="os")
    proficiency = relationship("ProficiencyLevel", foreign_keys=[proficiency_id])

class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    proficiency_id = Column(Integer, ForeignKey("proficiency_levels.id"))

    projects = relationship("ProjectLanguage", back_populates="language")
    proficiency = relationship("ProficiencyLevel", foreign_keys=[proficiency_id])

class Framework(Base):
    __tablename__ = "frameworks"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    proficiency_id = Column(Integer, ForeignKey("proficiency_levels.id"))

    projects = relationship("ProjectFramework", back_populates="framework")
    proficiency = relationship("ProficiencyLevel", foreign_keys=[proficiency_id])

class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    proficiency_id = Column(Integer, ForeignKey("proficiency_levels.id"))

    projects = relationship("ProjectTool", back_populates="tool")
    proficiency = relationship("ProficiencyLevel", foreign_keys=[proficiency_id])

class Cloud(Base):
    __tablename__ = "clouds"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    proficiency_id = Column(Integer, ForeignKey("proficiency_levels.id"))

    projects = relationship("ProjectCloud", back_populates="cloud")
    proficiency = relationship("ProficiencyLevel", foreign_keys=[proficiency_id])

class DB(Base):
    __tablename__ = "dbs"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    proficiency_id = Column(Integer, ForeignKey("proficiency_levels.id"))

    projects = relationship("ProjectDB", back_populates="db")
    proficiency = relationship("ProficiencyLevel", foreign_keys=[proficiency_id])

class Qualification(Base):
    __tablename__ = "qualifications"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    order_index = Column(Integer, default=0)  # 上位順序
    
    projects = relationship("Project", back_populates="role")
    engagements = relationship("Engagement", back_populates="role_override")
    project_roles = relationship("ProjectRole", back_populates="role")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    note = Column(Text)
    order_index = Column(Integer, default=0)  # 上流順序（工程順）
    
    projects = relationship("Project", back_populates="task")
    engagements = relationship("Engagement", back_populates="task_override")
    project_tasks = relationship("ProjectTask", back_populates="task")