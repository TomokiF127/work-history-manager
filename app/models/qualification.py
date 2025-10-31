from sqlalchemy import Column, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class UserQualification(Base):
    """ユーザーが取得した資格（取得年月付き）"""
    __tablename__ = "user_qualifications"
    
    id = Column(Integer, primary_key=True)
    qualification_id = Column(Integer, ForeignKey("qualifications.id"), nullable=False)
    obtained_date = Column(Date, nullable=False)  # 取得年月日
    note = Column(Text)  # 備考（認定番号など）
    
    qualification = relationship("Qualification")