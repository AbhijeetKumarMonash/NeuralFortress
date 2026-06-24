from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base

class Document(Base):
    __tablename__="documents"

    id = Column(Integer, primary_key =True, index=True)
    content = Column(Text, nullable=False)
    source = Column(String,nullable=True)

    #the mathematical representation of your data (1536 dimensions is standard for modern LLMs)
    embedding = Column(Vector(1536))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_index = Column(Integer, default=0)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    norm_name = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, default="OTHER")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    target_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    predicate = Column(String, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WatchedSource(Base):
    __tablename__ = "watched_sources"
    id           = Column(Integer, primary_key=True, index=True)
    url          = Column(String, nullable=False)
    label        = Column(String, nullable=True)         # friendly name for the UI
    last_hash    = Column(String, nullable=True)         # SHA-256 of last seen content (dedupe)
    last_checked = Column(DateTime(timezone=True), nullable=True)
    last_status  = Column(String, nullable=True)         # 'ok' | 'unchanged' | 'error: ...'
    active       = Column(Integer, default=1)            # 1 = polling, 0 = paused
    created_at   = Column(DateTime(timezone=True), server_default=func.now())