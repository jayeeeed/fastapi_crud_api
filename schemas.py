from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    price: int


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    name: str | None = None
    price: int | None = None


class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
