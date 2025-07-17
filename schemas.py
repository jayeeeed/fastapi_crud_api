from pydantic import BaseModel, Field, validator
from typing import Optional
import uuid


class ItemBase(BaseModel):
    name: str = Field(..., description="Item name is required")
    price: int = Field(..., description="Item price is required")


class ItemCreate(BaseModel):
    id: Optional[str] = Field(None, description="Item ID (UUID will be generated if not provided)")
    name: str = Field(..., description="Item name is required")
    price: int = Field(..., description="Item price is required")
    
    @validator('id', pre=True, always=True)
    def generate_id_if_missing(cls, v):
        if v is None or v == "":
            return str(uuid.uuid4())
        return v


class ItemUpdate(BaseModel):
    id: str = Field(..., description="Item ID is required for updates")
    name: str = Field(..., description="Item name is required")
    price: int = Field(..., description="Item price is required")


class Item(BaseModel):
    id: str = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    price: int = Field(..., description="Item price")

    class Config:
        from_attributes = True
