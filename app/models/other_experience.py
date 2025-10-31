from sqlalchemy import Column, Integer, Text, Date
from models.base import Base

class OtherExperience(Base):
    """その他経歴（学習・研修等）"""
    __tablename__ = "other_experiences"
    
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)  # タイトル
    content = Column(Text, nullable=False)  # 内容
    start_date = Column(Date)  # 開始年月日
    end_date = Column(Date)  # 終了年月日
    order_index = Column(Integer, default=0)  # 表示順序
    is_active = Column(Integer, default=1)  # 有効フラグ
    note = Column(Text)  # 備考