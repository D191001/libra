import time

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal, engine
from app.models import Base

app = FastAPI()


@app.on_event("startup")
async def startup():
    time.sleep(10)  # Добавьте задержку в 10 секунд
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(models.Author).count() == 0:
        example_author = models.Author(
            name="Default Author",
            biography="Default biography",
            birth_date="1970-01-01",
        )
        db.add(example_author)
        db.commit()
    db.close()


@app.on_event("shutdown")
async def shutdown():
    pass


# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD операции для книг
@app.post("/books/", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db=db, book=book)


@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def read_book(book_id: int, db: Session = Depends(get_db)):
    return crud.get_book(db=db, book_id=book_id)


@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)
):
    return crud.update_book(db=db, book_id=book_id, book=book)


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return crud.delete_book(db=db, book_id=book_id)


# CRUD операции для авторов
@app.post("/authors/", response_model=schemas.AuthorResponse)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    return crud.create_author(db=db, author=author)


@app.get("/authors/{author_id}", response_model=schemas.AuthorResponse)
def read_author(author_id: int, db: Session = Depends(get_db)):
    return crud.get_author(db=db, author_id=author_id)


@app.put("/authors/{author_id}", response_model=schemas.AuthorResponse)
def update_author(
    author_id: int, author: schemas.AuthorUpdate, db: Session = Depends(get_db)
):
    return crud.update_author(db=db, author_id=author_id, author=author)


@app.delete("/authors/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_db)):
    return crud.delete_author(db=db, author_id=author_id)
