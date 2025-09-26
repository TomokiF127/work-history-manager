from contextlib import contextmanager
from sqlalchemy.orm import Session
from models import init_db, get_session

class DatabaseService:
    def __init__(self):
        self.engine, self.SessionLocal = init_db()
    
    @contextmanager
    def session_scope(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session(self) -> Session:
        return self.SessionLocal()

db_service = DatabaseService()