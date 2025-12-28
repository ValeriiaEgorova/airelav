from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field

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