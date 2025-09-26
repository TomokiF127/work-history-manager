from sqlalchemy import Column, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from models.base import Base

class TechUsage(Base):
    __tablename__ = "tech_usages"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    kind = Column(Text, nullable=False)
    tech_id = Column(Integer, nullable=False)
    start = Column(Text)
    end = Column(Text)
    
    project = relationship("Project", back_populates="tech_usages")
    
    __table_args__ = (
        CheckConstraint("kind IN ('os', 'language', 'framework', 'tool', 'cloud', 'db')"),
    )