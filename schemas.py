from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    id: str
    name: str
    price: int


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class Item(ItemBase):
    class Config:
        from_attributes = True
