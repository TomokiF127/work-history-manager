from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

Base = declarative_base()
ENGINE = None
SessionLocal = None

def init_db(db_path=None):
    global ENGINE, SessionLocal
    
    # 設定ファイルから読み込み
    if db_path is None:
        from config import config
        db_path = config.get_database_path()
        echo = config.get_database_echo()
    else:
        echo = False
    
    # パスが相対パスの場合、プロジェクトルートからの相対パスとして扱う
    db_path = Path(db_path)
    if not db_path.is_absolute():
        # app/models/base.py から2つ上がプロジェクトルート
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / db_path
    
    # ディレクトリを作成
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    ENGINE = create_engine(f"sqlite:///{db_path}", echo=echo)
    
    @event.listens_for(ENGINE, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
    
    Base.metadata.create_all(bind=ENGINE)
    
    return ENGINE, SessionLocal

def get_session():
    if SessionLocal is None:
        init_db()
    return SessionLocal()