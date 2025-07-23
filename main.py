from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DisconnectionError
import models, schemas
from database import SessionLocal, engine
import os
import uuid
import uvicorn
import logging
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from health import health_start, health_stop

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test the connection
            db.execute("SELECT 1")
            yield db
            return
        except (OperationalError, DisconnectionError) as e:
            logger.warning(
                f"Database connection attempt {attempt + 1} failed: {str(e)}"
            )
            if db:
                db.close()
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All database connection attempts failed")
                raise HTTPException(
                    status_code=503, detail="Database connection failed"
                )
        except Exception as e:
            if db:
                db.close()
            logger.error(f"Unexpected database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
        finally:
            if "db" in locals():
                db.close()


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    logger.info(
        f"POST /items/ - Creating item with params: id={item.id}, user_id={item.user_id}, name={item.name}, price={item.price}"
    )
    db_item = models.Item(
        id=item.id, user_id=item.user_id, name=item.name, price=item.price
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    logger.info(f"POST /items/ - Successfully created item with id: {db_item.id}")
    return db_item


@app.get("/items/", response_model=list[schemas.Item])
def read_items(
    skip: int = 0, limit: int = 20, user_id: str = None, db: Session = Depends(get_db)
):
    logger.info(
        f"GET /items/ - Query params: skip={skip}, limit={limit}, user_id={user_id}"
    )
    query = db.query(models.Item)
    if user_id:
        query = query.filter(models.Item.user_id == user_id)
    items = query.offset(skip).limit(limit).all()
    logger.info(f"GET /items/ - Retrieved {len(items)} items")
    return items


@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: str, db: Session = Depends(get_db)):
    logger.info(f"GET /items/{item_id} - Path param: item_id={item_id}")
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        logger.warning(f"GET /items/{item_id} - Item not found")
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"GET /items/{item_id} - Successfully retrieved item: {item.name}")
    return item


@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: str, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    logger.info(
        f"PUT /items/{item_id} - Path param: item_id={item_id}, Body params: id={item.id}, user_id={item.user_id}, name={item.name}, price={item.price}"
    )
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        logger.warning(f"PUT /items/{item_id} - Item not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.id = item.id
    db_item.user_id = item.user_id
    db_item.name = item.name
    db_item.price = item.price
    db.commit()
    db.refresh(db_item)
    logger.info(f"PUT /items/{item_id} - Successfully updated item")
    return db_item


@app.patch("/items/{item_id}", response_model=schemas.Item)
def patch_item(item_id: str, item: schemas.ItemPatch, db: Session = Depends(get_db)):
    # Log only the provided fields
    provided_fields = {k: v for k, v in item.dict().items() if v is not None}
    logger.info(
        f"PATCH /items/{item_id} - Path param: item_id={item_id}, Body params: {provided_fields}"
    )

    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        logger.warning(f"PATCH /items/{item_id} - Item not found")
        raise HTTPException(status_code=404, detail="Item not found")

    # Only update fields that are provided (not None)
    if item.id is not None:
        db_item.id = item.id
    if item.user_id is not None:
        db_item.user_id = item.user_id
    if item.name is not None:
        db_item.name = item.name
    if item.price is not None:
        db_item.price = item.price

    db.commit()
    db.refresh(db_item)
    logger.info(
        f"PATCH /items/{item_id} - Successfully patched item with fields: {list(provided_fields.keys())}"
    )
    return db_item


@app.delete("/items/{item_id}")
def delete_item(item_id: str, db: Session = Depends(get_db)):
    logger.info(f"DELETE /items/{item_id} - Path param: item_id={item_id}")
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        logger.warning(f"DELETE /items/{item_id} - Item not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    logger.info(f"DELETE /items/{item_id} - Successfully deleted item")
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
