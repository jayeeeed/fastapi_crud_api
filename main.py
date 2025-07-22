from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine
import os
import uuid
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from health import health_start, health_stop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    health_start()
    yield

    # Shutdown logic
    health_stop()


app = FastAPI(lifespan=lifespan)

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(
        id=item.id, user_id=item.user_id, name=item.name, price=item.price
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/items/", response_model=list[schemas.Item])
def read_items(
    skip: int = 0, limit: int = 20, user_id: str = None, db: Session = Depends(get_db)
):
    query = db.query(models.Item)
    if user_id:
        query = query.filter(models.Item.user_id == user_id)
    return query.offset(skip).limit(limit).all()


@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: str, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.id = item.id
    db_item.user_id = item.user_id
    db_item.name = item.name
    db_item.price = item.price
    db.commit()
    db.refresh(db_item)
    return db_item


@app.patch("/items/{item_id}", response_model=schemas.Item)
def patch_item(item_id: str, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.id = item.id
    db_item.user_id = item.user_id
    db_item.name = item.name
    db_item.price = item.price
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/items/{item_id}")
def delete_item(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"detail": "Item deleted"}


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
