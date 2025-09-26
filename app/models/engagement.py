from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Engagement(Base):
    __tablename__ = "engagements"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    site_start = Column(Text, nullable=False)
    site_end = Column(Text)
    role_override_id = Column(Integer, ForeignKey("roles.id"))
    task_override_id = Column(Integer, ForeignKey("tasks.id"))
    scale_override_text = Column(Text)
    
    project = relationship("Project", back_populates="engagements")
    role_override = relationship("Role", back_populates="engagements")
    task_override = relationship("Task", back_populates="engagements")