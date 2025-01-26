import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if __name__ == "__main__" and __package__ is None:
    import sys
    from os.path import dirname, abspath
    sys.path.insert(0, dirname(dirname(abspath(__file__))))
    __package__ = "tests"

from ..app.main import app
from ..app.database import Base, get_db
from ..app.schemas import UserCreate, AuthorCreate, BookCreate, BookIssueCreate

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def create_user():
    user_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/users/", json=user_data)
    return response.json()

def test_create_user():
    user_data = {"username": "testuser2", "password": "testpassword2"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser2"

def test_login_for_access_token(create_user):
    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_author(create_user):
    author_data = {"name": "Author Name", "biography": "Author Biography", "birth_date": "2000-01-01"}
    response = client.post("/authors/", json=author_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Author Name"

def test_create_book(create_user):
    author_data = {"name": "Author Name", "biography": "Author Biography", "birth_date": "2000-01-01"}
    author_response = client.post("/authors/", json=author_data)
    author_id = author_response.json()["id"]

    book_data = {
        "title": "Book Title",
        "description": "Book Description",
        "publication_date": "2021-01-01",
        "available_copies": 5,
        "author_id": author_id
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Book Title"

def test_create_book_issue(create_user):
    author_data = {"name": "Author Name", "biography": "Author Biography", "birth_date": "2000-01-01"}
    author_response = client.post("/authors/", json=author_data)
    author_id = author_response.json()["id"]

    book_data = {
        "title": "Book Title",
        "description": "Book Description",
        "publication_date": "2021-01-01",
        "available_copies": 5,
        "author_id": author_id
    }
    book_response = client.post("/books/", json=book_data)
    book_id = book_response.json()["id"]

    book_issue_data = {
        "user_id": create_user["id"],
        "book_id": book_id,
        "issue_date": "2021-01-01",
        "expected_return_date": "2021-02-01"
    }
    response = client.post("/book_issues/", json=book_issue_data)
    assert response.status_code == 200
    assert response.json()["book_id"] == book_id