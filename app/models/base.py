from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()
ENGINE = None
SessionLocal = None

def init_db(db_path="./data/skills.db"):
    global ENGINE, SessionLocal
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    ENGINE = create_engine(f"sqlite:///{db_path}", echo=False)
    
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