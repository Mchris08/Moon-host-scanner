from sqlalchemy import (create_engine, Column, Integer, String, Boolean,
                        DateTime, ForeignKey, Text, Float)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///./app.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    is_verified = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ScanJob(Base):
    __tablename__ = "scan_jobs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    region = Column(String, default="zim")
    status = Column(String, default="pending")
    summary_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class HostSubmission(Base):
    __tablename__ = "host_submissions"
    id = Column(Integer, primary_key=True)
    scan_job_id = Column(Integer, ForeignKey("scan_jobs.id"), nullable=True)
    host = Column(String, nullable=False, index=True)
    port = Column(Integer, nullable=False)
    score = Column(Integer, default=0)
    grade = Column(String, default="F")
    tunnel_ready = Column(Boolean, default=False)
    is_zimbabwe = Column(Boolean, default=True)
    status = Column(String, default="pending")
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)
