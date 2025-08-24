from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base

_engine = None
SessionLocal = None

def _normalize_postgres_dsn(dsn: str) -> str:
    # 统一切换到 psycopg 3 的 SQLAlchemy 方言，避免误用 psycopg2 或默认驱动
    if dsn.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + dsn[len("postgresql+psycopg2://"):]
    if dsn.startswith("postgresql://"):
        return "postgresql+psycopg://" + dsn[len("postgresql://"):]
    return dsn

def init_engine_and_create_tables():
    global _engine, SessionLocal
    dsn = _normalize_postgres_dsn(settings.POSTGRES_DSN)
    _engine = create_engine(dsn, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    Base.metadata.create_all(bind=_engine)

def get_db():
    global SessionLocal
    if SessionLocal is None:
        init_engine_and_create_tables()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()