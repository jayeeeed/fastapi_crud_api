from sqlalchemy import Column, Integer, String
from database import Base
import uuid


class Item(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Integer, nullable=False)
