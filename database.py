import os
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session

load_dotenv()

sqlite_url = os.getenv("DATABASE_URL", "sqlite:///database.db")
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session