from datetime import date
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


class AuthorBase(BaseModel):
    name: str
    biography: str
    birth_date: date


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    pass


class AuthorResponse(AuthorBase):
    id: int

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    title: str
    description: str
    publication_date: date
    available_copies: int
    author_id: int


# Убедитесь, что нет устаревшего синтаксиса Python 2
class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookResponse(BookBase):
    id: int

    class Config:
        orm_mode = True


class BookIssueBase(BaseModel):
    user_id: int
    book_id: int
    issue_date: date
    expected_return_date: date


class BookIssueCreate(BookIssueBase):
    pass


class BookIssueUpdate(BaseModel):
    return_date: Optional[date] = None


class BookIssueResponse(BookIssueBase):
    id: int
    return_date: Optional[date] = None

    class Config:
        orm_mode = True
