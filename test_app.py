from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .main import app
from .database import Base, get_db


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

pytest.test_key = ""
pytest.test_secret_key = ""
pytest.target_url_valid = "http://google.com"


def test_create_url():
    response = client.post(
        "/url", json={"target_url": pytest.target_url_valid})
    data = response.json()

    pytest.test_key = data['url']
    pytest.test_secret_key = data['admin_url']

    assert response.status_code == 200
    assert 'admin_url' in data.keys() and 'url' in data.keys()
    assert data['target_url'] == pytest.target_url_valid


def test_create_url_validation_error():
    invalid_url = "thisisnotanurl123"
    response = client.post("/url", json={"target_url": invalid_url})
    data = response.json()

    assert response.status_code == 400
    assert data['detail'] == "Please provide a valid url"


def test_get_redirect_url():
    # since its a redirect response we have to test it like this (307 temporary redirect)
    response = client.get(pytest.test_key, allow_redirects=False)
    assert response.status_code == 307


def test_get_404_url():
    response = client.get("/NOTFOUND")
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"URL 'http://testserver/NOTFOUND' doesn't exist."
    }


def test_graceful_forward_url():
    not_valid_url = "http://this.should.not.be.a.site.io"
    response = client.post("/url", json={"target_url": not_valid_url})
    data = response.json()
    url_key = data['url']

    assert response.status_code == 200
    assert 'admin_url' in data.keys() and 'url' in data.keys()
    assert data['target_url'] == not_valid_url

    response = client.get(url_key)
    assert response.status_code == 404


def test_peek_url():
    key = pytest.test_key[-5:len(pytest.test_key)]
    response = client.get(f"/peek/{key}")
    assert response.status_code == 200
    assert response.json() == pytest.target_url_valid


def test_peek_url_404():
    response = client.get("/peek/INVALID")
    assert response.status_code == 404


def test_get_url_info():
    response = client.get(pytest.test_secret_key)
    data = response.json()
    assert response.status_code == 200
    assert 'admin_url' in data.keys() and 'url' in data.keys()
    assert data['target_url'] == pytest.target_url_valid


def test_get_url_info_404():
    response = client.get("/admin/NOTFOUND")

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"URL 'http://testserver/admin/NOTFOUND' doesn't exist."
    }


def test_delete_url():
    print(pytest.test_secret_key)
    response = client.delete(pytest.test_secret_key)

    assert response.status_code == 200

    response = client.get(pytest.test_key)
    assert response.status_code == 404


def test_delete_url_404():
    response = client.delete("/admin/NOTFOUND")

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"URL 'http://testserver/admin/NOTFOUND' doesn't exist."
    }
