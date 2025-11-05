from sqlalchemy import Column, Integer, Text
from models.base import Base

class ProficiencyLevel(Base):
    """習熟度レベルマスタ"""
    __tablename__ = "proficiency_levels"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)  # 習熟度名（例：通常使用に問題なし）
    note = Column(Text)  # 備考
    order_index = Column(Integer, default=0)  # 表示順序
