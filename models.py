from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import Column, JSON

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    
    tasks: List["GenerationTask"] = Relationship(back_populates="user")

class GenerationTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt: str
    file_format: str
    status: str = "pending"
    progress: int = 0
    status_message: str = "Ожидание"
    
    generated_code: Optional[str] = None
    file_path: Optional[str] = None
    error_log: Optional[str] = None
    preview_data: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="tasks")