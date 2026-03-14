from sqlalchemy import Column,Integer,String,Text,DateTime
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

