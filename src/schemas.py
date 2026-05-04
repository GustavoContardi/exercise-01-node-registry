"""
Pydantic schemas for request/response validation.

NodeCreate: for POST body (name, host, port — all required)
NodeUpdate: for PUT body (host, port — optional)
NodeResponse: for API responses (includes id, status, timestamps)
"""

# TODO: Implement your Pydantic schemas here

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class NodeCreate(BaseModel):
    name: str = Field(..., min_length=1)
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)


class NodeUpdate(BaseModel):
    host: Optional[str] = Field(None, min_length=1)
    port: Optional[int] = Field(None, ge=1, le=65535)


class NodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    host: str
    port: int
    status: str
    created_at: datetime
    updated_at: datetime


class HealthOut(BaseModel):
    status: str
    db: str
    nodes_count: int