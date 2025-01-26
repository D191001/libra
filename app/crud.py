import logging

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка логирования
logger = logging.getLogger(__name__)


def get_user_by_username(db: Session, username: str):
    user = (
        db.query(models.User).filter(models.User.username == username).first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User {db_user.username} created")
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password"
        )
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=401, detail="Incorrect username or password"
        )
    return user


# CRUD операции для авторов
def create_author(db: Session, author: schemas.AuthorCreate):
    db_author = models.Author(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    logger.info(f"Author {db_author.name} created")
    return db_author


def get_author(db: Session, author_id: int):
    author = (
        db.query(models.Author).filter(models.Author.id == author_id).first()
    )
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


def update_author(db: Session, author_id: int, author: schemas.AuthorUpdate):
    db_author = (
        db.query(models.Author).filter(models.Author.id == author_id).first()
    )
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    for key, value in author.dict().items():
        setattr(db_author, key, value)
    db.commit()
    db.refresh(db_author)
    logger.info(f"Author {db_author.name} updated")
    return db_author


def delete_author(db: Session, author_id: int):
    db_author = (
        db.query(models.Author).filter(models.Author.id == author_id).first()
    )
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(db_author)
    db.commit()
    logger.info(f"Author with ID {author_id} deleted")
    return {"detail": "Author deleted"}


def get_authors(
    db: Session, skip: int = 0, limit: int = 10, search: str = None
):
    query = db.query(models.Author)
    if search:
        query = query.filter(
            or_(
                models.Author.name.ilike(f"%{search}%"),
                models.Author.biography.ilike(f"%{search}%"),
            )
        )
    return query.offset(skip).limit(limit).all()


# CRUD операции для книг
def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    logger.info(f"Book {db_book.title} created")
    return db_book


def get_book(db: Session, book_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def update_book(db: Session, book_id: int, book: schemas.BookUpdate):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    logger.info(f"Book {db_book.title} updated")
    return db_book


def delete_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    logger.info(f"Book with ID {book_id} deleted")
    return {"detail": "Book deleted"}


def get_books(db: Session, skip: int = 0, limit: int = 10, search: str = None):
    query = db.query(models.Book)
    if search:
        query = query.filter(
            or_(
                models.Book.title.ilike(f"%{search}%"),
                models.Book.description.ilike(f"%{search}%"),
            )
        )
    return query.offset(skip).limit(limit).all()


# CRUD операции для выдачи книг
def create_book_issue(db: Session, book_issue: schemas.BookIssueCreate):
    db_book_issue = models.BookIssue(**book_issue.dict())
    db.add(db_book_issue)
    db.commit()
    db.refresh(db_book_issue)
    logger.info(
        f"Book with ID {db_book_issue.book_id} issued to user with ID {db_book_issue.user_id}"
    )
    return db_book_issue


def update_book_issue(
    db: Session, book_issue_id: int, book_issue: schemas.BookIssueUpdate
):
    db_book_issue = (
        db.query(models.BookIssue)
        .filter(models.BookIssue.id == book_issue_id)
        .first()
    )
    if not db_book_issue:
        raise HTTPException(status_code=404, detail="Book issue not found")
    if book_issue.return_date:
        db_book_issue.return_date = book_issue.return_date
    db.commit()
    db.refresh(db_book_issue)
    logger.info(f"Book issue with ID {book_issue_id} updated")
    return db_book_issue


def get_book_issues(db: Session, user_id: int):
    return (
        db.query(models.BookIssue)
        .filter(models.BookIssue.user_id == user_id)
        .all()
    )
