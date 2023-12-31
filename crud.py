from sqlalchemy.orm import Session

from .keygen import generate_key
from . import models, schemas


def get_db_url_by_key(db: Session, url_key: str) -> models.URL:
    return (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )


def create_db_url(db: Session, url: schemas.URLBase) -> models.URL:
    key = generate_key()

    # check if key doesn't already exist
    while get_db_url_by_key(db, key):
        key = generate_key()

    secret_key = f"{key}_{generate_key(8)}"
    # create url model
    db_url = models.URL(
        target_url=url.target_url, key=key, secret_key=secret_key
    )
    # add url obj to db
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL:
    return (
        db.query(models.URL)
        .filter(models.URL.secret_key == secret_key, models.URL.is_active)
        .first()
    )


def update_clicks(db: Session, db_url: schemas.URL) -> models.URL:
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url


def delete_url_by_secret_id(db: Session, secret_key: str) -> models.URL:
    db_url = get_db_url_by_secret_key(db, secret_key)
    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
    return db_url


def delete_url_by_key(db: Session, url_key: str) -> models.URL:
    db_url = get_db_url_by_key(db, url_key)
    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
    return db_url
