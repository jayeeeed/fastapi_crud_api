from pydantic import BaseModel, Field
from typing import Optional
import uuid


class ItemBase(BaseModel):
    name: str = Field(..., description="Item name is required")
    price: int = Field(..., description="Item price is required")


class ItemCreate(ItemBase):
    id: Optional[str] = Field(
        None, description="Item ID (UUID will be generated if not provided)"
    )


class ItemUpdate(ItemBase):
    id: str = Field(..., description="Item ID is required for updates")


class Item(ItemBase):
    id: str = Field(..., description="Item ID")

    class Config:
        from_attributes = True
