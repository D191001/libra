import time
from datetime import date

from databases import Database
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

DATABASE_URL = "postgresql://myuser:mypassword@db:5432/libradata"

database = Database(DATABASE_URL)
metadata = MetaData()

Base = declarative_base()


# Определение моделей
class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    publication_date = Column(Date)
    available_copies = Column(Integer)
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship("Author")
    genres = relationship("Genre", secondary="book_genres")


book_genres = Table(
    'book_genres',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id')),
    Column('genre_id', Integer, ForeignKey('genres.id')),
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


@app.on_event("startup")
async def startup():
    time.sleep(10)  # Добавьте задержку в 10 секунд
    await database.connect()
    Base.metadata.create_all(bind=engine)

    # Добавление одного автора
    db = SessionLocal()
    if db.query(Author).count() == 0:
        example_author = Author(name="Default Author")
        db.add(example_author)
        db.commit()
    db.close()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Pydantic схемы
class BookCreate(BaseModel):
    title: str
    description: str
    publication_date: date
    available_copies: int
    author_id: int


class BookUpdate(BaseModel):
    title: str
    description: str
    publication_date: date
    available_copies: int
    author_id: int


class BookResponse(BaseModel):
    id: int
    title: str
    description: str
    publication_date: date
    available_copies: int
    author_id: int

    class Config:
        orm_mode = True


# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD операции
@app.post("/books/", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    # Проверка существования автора
    author = db.query(Author).filter(Author.id == book.author_id).first()
    if author is None:
        raise HTTPException(status_code=400, detail="Author not found")

    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"detail": "Book deleted"}


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
