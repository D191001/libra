import logging
import time
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal, engine
from app.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_active_user,
    get_current_admin_user,
    get_db,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def startup():
    time.sleep(10)  # Добавьте задержку в 10 секунд
    models.Base.metadata.create_all(bind=engine)
    logger.info("Application startup complete")


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"User {user.username} logged in")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = crud.create_user(db=db, user=user)
    logger.info(f"User {new_user.username} created")
    return new_user


@app.get("/users/me/", response_model=schemas.UserResponse)
def read_users_me(
    current_user: models.User = Depends(get_current_active_user),
):
    return current_user


@app.put("/users/me/", response_model=schemas.UserResponse)
def update_user_me(
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    updated_user = crud.update_user(db=db, user_id=current_user.id, user=user)
    logger.info(f"User {current_user.username} updated their information")
    return updated_user


@app.get(
    "/users/",
    response_model=list[schemas.UserResponse],
    dependencies=[Depends(get_current_admin_user)],
)
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db=db)


# CRUD операции для авторов
@app.post(
    "/authors/",
    response_model=schemas.AuthorResponse,
    dependencies=[Depends(get_current_admin_user)],
)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    new_author = crud.create_author(db=db, author=author)
    logger.info(f"Author {new_author.name} created")
    return new_author


@app.get("/authors/{author_id}", response_model=schemas.AuthorResponse)
def read_author(author_id: int, db: Session = Depends(get_db)):
    return crud.get_author(db=db, author_id=author_id)


@app.put(
    "/authors/{author_id}",
    response_model=schemas.AuthorResponse,
    dependencies=[Depends(get_current_admin_user)],
)
def update_author(
    author_id: int, author: schemas.AuthorUpdate, db: Session = Depends(get_db)
):
    updated_author = crud.update_author(
        db=db, author_id=author_id, author=author
    )
    logger.info(f"Author {updated_author.name} updated")
    return updated_author


@app.delete(
    "/authors/{author_id}", dependencies=[Depends(get_current_admin_user)]
)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    result = crud.delete_author(db=db, author_id=author_id)
    logger.info(f"Author with ID {author_id} deleted")
    return result


@app.get("/authors/", response_model=list[schemas.AuthorResponse])
def read_authors(
    skip: int = 0,
    limit: int = 10,
    search: str = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_authors(db=db, skip=skip, limit=limit, search=search)


# CRUD операции для книг
@app.post(
    "/books/",
    response_model=schemas.BookResponse,
    dependencies=[Depends(get_current_admin_user)],
)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    new_book = crud.create_book(db=db, book=book)
    logger.info(f"Book {new_book.title} created")
    return new_book


@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def read_book(book_id: int, db: Session = Depends(get_db)):
    return crud.get_book(db=db, book_id=book_id)


@app.put(
    "/books/{book_id}",
    response_model=schemas.BookResponse,
    dependencies=[Depends(get_current_admin_user)],
)
def update_book(
    book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)
):
    updated_book = crud.update_book(db=db, book_id=book_id, book=book)
    logger.info(f"Book {updated_book.title} updated")
    return updated_book


@app.delete("/books/{book_id}", dependencies=[Depends(get_current_admin_user)])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    result = crud.delete_book(db=db, book_id=book_id)
    logger.info(f"Book with ID {book_id} deleted")
    return result


@app.get("/books/", response_model=list[schemas.BookResponse])
def read_books(
    skip: int = 0,
    limit: int = 10,
    search: str = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_books(db=db, skip=skip, limit=limit, search=search)


# Маршруты для выдачи книг
@app.post(
    "/book_issues/",
    response_model=schemas.BookIssueResponse,
    dependencies=[Depends(get_current_active_user)],
)
def create_book_issue(
    book_issue: schemas.BookIssueCreate, db: Session = Depends(get_db)
):
    new_issue = crud.create_book_issue(db=db, book_issue=book_issue)
    logger.info(
        f"Book with ID {new_issue.book_id} issued to user with ID {new_issue.user_id}"
    )
    return new_issue


@app.put(
    "/book_issues/{book_issue_id}",
    response_model=schemas.BookIssueResponse,
    dependencies=[Depends(get_current_active_user)],
)
def update_book_issue(
    book_issue_id: int,
    book_issue: schemas.BookIssueUpdate,
    db: Session = Depends(get_db),
):
    updated_issue = crud.update_book_issue(
        db=db, book_issue_id=book_issue_id, book_issue=book_issue
    )
    logger.info(f"Book issue with ID {book_issue_id} updated")
    return updated_issue


@app.get(
    "/book_issues/",
    response_model=list[schemas.BookIssueResponse],
    dependencies=[Depends(get_current_active_user)],
)
def read_book_issues(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return crud.get_book_issues(db=db, user_id=current_user.id)
