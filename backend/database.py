import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

#Load your secret connection string from the .env file 
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to NEON  Database 
engine=create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False , bind=engine)

#This is the base class for your database tables
Base = declarative_base()

#Dependency to open and close the connection safely
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()