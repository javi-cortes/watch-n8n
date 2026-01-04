import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from sqlalchemy import select, desc, text
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import WorkflowWatcher
from .schemas import WorkflowWatcherIn, WorkflowWatcherOut, WorkflowWatcherListOut

API_KEY = os.getenv("API_KEY", "")


def require_api_key(x_api_key: str | None = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


def init_db_with_retry(max_attempts: int = 30, sleep_seconds: float = 1.0) -> None:
    last_exc: Exception | None = None
    for _ in range(max_attempts):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            return
        except Exception as e:
            last_exc = e
            time.sleep(sleep_seconds)
    if last_exc:
        raise last_exc


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_with_retry()
    yield


app = FastAPI(
    title="watch-n8n",
    description="Workflow watchers store extra execution data around n8n workflows and nodes",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"service": "watch-n8n", "status": "ok"}


@app.post(
    "/workflow-watchers",
    response_model=WorkflowWatcherOut,
    dependencies=[Depends(require_api_key)],
)
def create_workflow_watcher(body: WorkflowWatcherIn, db: Session = Depends(get_db)):
    row = WorkflowWatcher(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get(
    "/workflow-watchers/{id}",
    response_model=WorkflowWatcherOut,
    dependencies=[Depends(require_api_key)],
)
def get_workflow_watcher(id: int, db: Session = Depends(get_db)):
    row = db.get(WorkflowWatcher, id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row


@app.get(
    "/workflow-watchers",
    response_model=WorkflowWatcherListOut,
    dependencies=[Depends(require_api_key)],
)
def list_workflow_watchers(
    workflow_id: str | None = Query(default=None),
    execution_id: str | None = Query(default=None),
    node_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    cursor: int
    | None = Query(default=None, description="Pagination cursor: last seen id"),
    db: Session = Depends(get_db),
):
    stmt = select(WorkflowWatcher)

    if workflow_id:
        stmt = stmt.where(WorkflowWatcher.workflow_id == workflow_id)
    if execution_id:
        stmt = stmt.where(WorkflowWatcher.execution_id == execution_id)
    if node_id:
        stmt = stmt.where(WorkflowWatcher.node_id == node_id)

    stmt = stmt.order_by(desc(WorkflowWatcher.id))

    if cursor is not None:
        stmt = stmt.where(WorkflowWatcher.id < cursor)

    stmt = stmt.limit(limit + 1)

    rows = db.execute(stmt).scalars().all()

    next_cursor = None
    if len(rows) > limit:
        next_cursor = rows[limit - 1].id
        rows = rows[:limit]

    return {"items": rows, "next_cursor": next_cursor}
