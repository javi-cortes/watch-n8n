from sqlalchemy import String, DateTime, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class WorkflowWatcher(Base):
    __tablename__ = "workflow_watchers"

    id: Mapped[int] = mapped_column(primary_key=True)

    workflow_id: Mapped[str] = mapped_column(String(128), index=True)
    execution_id: Mapped[str | None] = mapped_column(
        String(128), index=True, nullable=True
    )
    node_id: Mapped[str | None] = mapped_column(String(256), index=True, nullable=True)

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    __table_args__ = (
        Index("ix_workflow_watchers_workflow_execution", "workflow_id", "execution_id"),
    )
