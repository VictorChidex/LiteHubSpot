from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
import uuid
from .sqlalchemy_db import Base


def _uuid_col():
    try:
        # Use PostgreSQL UUID type when available
        return Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    except Exception:
        # Fallback to string UUID
        return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class Todo(Base):
    __tablename__ = 'api_todo_sql'

    id = _uuid_col()
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, default='')
    due_date = Column(String(64), nullable=True)
    due_time = Column(String(64), nullable=True)
    start_date = Column(String(64), nullable=True)
    priority = Column(String(32), default='normal')
    status = Column(String(32), default='to_do')
    resolved = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self, include_user=False, user_obj=None):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'due_time': self.due_time,
            'start_date': self.start_date,
            'priority': self.priority,
            'status': self.status,
            'resolved': self.resolved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': user_obj or {'id': self.user_id}
        }
