from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List
from datetime import datetime


class WorkflowWatcherIn(BaseModel):
    workflow_id: str = Field(..., min_length=1)
    execution_id: Optional[str] = None
    node_id: Optional[str] = None
    payload: Dict[str, Any]


class WorkflowWatcherOut(BaseModel):
    id: int
    workflow_id: str
    execution_id: Optional[str]
    node_id: Optional[str]
    payload: Dict[str, Any]
    created_at: datetime


class WorkflowWatcherListOut(BaseModel):
    items: List[WorkflowWatcherOut]
    next_cursor: Optional[int] = None
