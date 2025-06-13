from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4

class PostBase(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    score: Optional[float] = None  # Search relevance score

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class SearchQuery(BaseModel):
    query: str
    tags: Optional[List[str]] = None
    page: int = 1
    size: int = 10
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"

class SearchResponse(BaseModel):
    total: int
    hits: List[Post]
    page: int
    size: int
    took_ms: Optional[int] = None  # Search execution time 