from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid


class ItemBase(BaseModel):
    id: str = Field(..., description="Item ID is required")
    user_id: str = Field(..., description="User ID is required")
    name: str = Field(..., description="Item name is required")
    price: int = Field(..., description="Item price is required")


class ItemCreate(BaseModel):
    id: Optional[str] = Field(
        None, description="Item ID (UUID will be generated if not provided)"
    )
    user_id: str = Field(..., description="User ID is required")
    name: str = Field(..., description="Item name is required")
    price: int = Field(..., description="Item price is required")

    @field_validator("id", mode="before")
    @classmethod
    def generate_id_if_missing(cls, v):
        if v is None or v == "":
            return str(uuid.uuid4())
        return v


class ItemUpdate(ItemBase):
    pass


class ItemPatch(BaseModel):
    id: Optional[str] = Field(None, description="Item ID (optional for patch)")
    user_id: Optional[str] = Field(None, description="User ID (optional for patch)")
    name: Optional[str] = Field(None, description="Item name (optional for patch)")
    price: Optional[int] = Field(None, description="Item price (optional for patch)")


class Item(ItemBase):
    class Config:
        from_attributes = True
