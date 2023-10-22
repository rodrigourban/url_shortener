from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.datastructures import URL
import validators
import httplib2

from .database import SessionLocal, engine
from . import models, schemas, crud
from .config import get_settings

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

def raise_not_found(request):
  message = f"URL '{request.url}' doesn't exist."
  raise HTTPException(
    status_code=404,
    detail=message
  )

def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
  base_url = URL(get_settings().base_url)
  admin_endpoint = app.url_path_for(
    "administration info", secret_key=db_url.secret_key
  )
  db_url.url = str(base_url.replace(path=db_url.key))
  db_url.admin_url = str(base_url.replace(path=admin_endpoint))
  return db_url

def forward_site_exists(forward_url) -> bool:
  # Graceful Forward: Check if the website exists before forwarding.
  # Check if sites exists before redirecting
  try:
    http = httplib2.Http()
    response = http.request(forward_url, 'HEAD')
    return int(response[0]['status']) < 400
  except:
    return False

@app.get("/{url_key}")
def forward_to_target(
  url_key: str,
  request: Request,
  db: Session = Depends(get_db)
):
  db_url = (
    db.query(models.URL)
    .filter(models.URL.key == url_key, models.URL.is_active)
    .first()
  )
  if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
    if forward_site_exists(db_url.target_url):
      crud.update_clicks(db=db, db_url=db_url)
      return RedirectResponse(db_url.target_url)
    else:
      # deactivate url if page does not exist
      crud.delete_url_by_key(db, url_key)
      raise_not_found(request)
  else:
    raise_not_found(request)


def raise_bad_request(message):
  raise HTTPException(
    status_code=400,
    detail=message
  )

@app.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
  # depends create a context that opens/closes db connection for request
  if not validators.url(url.target_url):
    raise_bad_request(message="Please provide a valid url")
  
  db_url = crud.create_db_url(db=db, url=url)

  return get_admin_info(db_url)


@app.get("/admin/{secret_key}", name="administration info", response_model=schemas.URLInfo)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
  if db_url := crud.get_db_url_by_secret_key(db, secret_key=secret_key):
    return get_admin_info(db_url)
  else:
    raise_not_found(request)
  

@app.delete("/admin/{secret_key}")
def delete_url(
  secret_key: str,
  request: Request,
  db: Session = Depends(get_db)
):
  if db_url := crud.delete_url_by_secret_id(db=db, secret_key=secret_key):
    message = f"Successfully deleted URL for {db_url.target_url}"
    return {
      "detail": message
    }
  else:
    raise_not_found(request)

@app.get("/peek/{url_key}")
def peek_url(url_key: str, request: Request, db: Session = Depends(get_db)):
  # Peek URL: Create an endpoint for your users to check which target URL is behind a shortened URL.
  if db_url := crud.get_db_url_by_key(db, url_key):
    return db_url.target_url
  else:
    raise_not_found(request)


