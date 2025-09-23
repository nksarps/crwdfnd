import uuid

from app.config.database import Base

from sqlalchemy import Column, UUID, DateTime
from sqlalchemy.sql import func


class BaseModel(Base):
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True, 
        unique=True,
        default=uuid.uuid4,
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())



