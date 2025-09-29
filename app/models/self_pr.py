from sqlalchemy import Column, Integer, Text, Boolean
from models.base import Base

class SelfPR(Base):
    __tablename__ = "self_prs"
    
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)  # タイトル（例：リーダー経験、技術力など）
    content = Column(Text, nullable=False)  # 内容
    order_index = Column(Integer, default=0)  # 表示順序
    is_active = Column(Boolean, default=True)  # 有効/無効