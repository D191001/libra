from datetime import date

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    return (
        db.query(models.User).filter(models.User.username == username).first()
    )


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_book_issue(db: Session, book_issue: schemas.BookIssueCreate):
    # Проверка количества одновременно выдаваемых книг
    active_issues = (
        db.query(models.BookIssue)
        .filter(
            models.BookIssue.user_id == book_issue.user_id,
            models.BookIssue.return_date == None,
        )
        .count()
    )
    if active_issues >= 5:
        raise HTTPException(
            status_code=400, detail="User already has 5 active book issues"
        )

    # Проверка доступных экземпляров книги
    book = (
        db.query(models.Book)
        .filter(models.Book.id == book_issue.book_id)
        .first()
    )
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=400, detail="No available copies of the book"
        )

    # Создание записи о выдаче книги
    db_book_issue = models.BookIssue(**book_issue.dict())
    db.add(db_book_issue)

    # Обновление количества доступных экземпляров книги
    book.available_copies -= 1
    db.commit()
    db.refresh(db_book_issue)
    return db_book_issue


def update_book_issue(
    db: Session, book_issue_id: int, book_issue: schemas.BookIssueUpdate
):
    db_book_issue = (
        db.query(models.BookIssue)
        .filter(models.BookIssue.id == book_issue_id)
        .first()
    )
    if db_book_issue is None:
        raise HTTPException(status_code=404, detail="Book issue not found")

    if book_issue.return_date:
        db_book_issue.return_date = book_issue.return_date

        # Обновление количества доступных экземпляров книги
        book = (
            db.query(models.Book)
            .filter(models.Book.id == db_book_issue.book_id)
            .first()
        )
        book.available_copies += 1

    db.commit()
    db.refresh(db_book_issue)
    return db_book_issue


def get_book_issues(db: Session, user_id: int):
    return (
        db.query(models.BookIssue)
        .filter(models.BookIssue.user_id == user_id)
        .all()
    )


# CRUD операции для авторов и книг остаются без изменений
