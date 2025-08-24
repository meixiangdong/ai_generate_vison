from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, func
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Script(Base):
    __tablename__ = "scripts"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True, nullable=True)
    prompt = Column(Text, nullable=False)
    content = Column(JSONB, nullable=False)  # list of segments
    created_at = Column(DateTime, server_default=func.now())

class Timeline(Base):
    __tablename__ = "timelines"
    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, index=True, nullable=False)
    items = Column(JSONB, nullable=False)  # list of {index, asset_path, caption, start, duration}
    created_at = Column(DateTime, server_default=func.now())

class Render(Base):
    __tablename__ = "renders"
    id = Column(Integer, primary_key=True, index=True)
    timeline_id = Column(Integer, index=True, nullable=False)
    kind = Column(String(50), nullable=False)  # preview or export
    video_path = Column(String(1024), nullable=False)
    srt_path = Column(String(1024), nullable=True)
    cover_path = Column(String(1024), nullable=True)
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(1024), nullable=False, unique=True)
    kind = Column(String(50), nullable=False)  # image|video|audio
    meta = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now())