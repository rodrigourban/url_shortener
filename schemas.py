from typing import Optional
from pydantic import BaseModel


class URLBase(BaseModel):
    # real url that you want to redirect to
    target_url: str


class URL(URLBase):
    is_active: bool
    clicks: int

    class Config:
        from_attributes = True


class URLInfo(URL):
    # we add these field in a child of URL because we are not storing
    # these values
    url: str
    admin_url: str
