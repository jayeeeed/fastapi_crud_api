from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid


class Item(Base):
    __tablename__ = "items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Integer, nullable=False)
