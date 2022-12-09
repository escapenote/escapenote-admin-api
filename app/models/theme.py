from typing import List, Optional
from pydantic import BaseModel, Field
from prisma import models

from app.models.cafe import Cafe


class Theme(models.Theme, warn_subclass=False):
    cafe: Optional[Cafe]


class ThemeListRes(BaseModel):
    total: int
    items: List[Theme]


class ThemeDetailRes(BaseModel):
    __root__: Theme


class CreateThemeDto(BaseModel):
    cafeId: str
    name: str
    intro: str
    thumbnail: Optional[str] = Field("")
    genre: Optional[str] = Field("")
    price: Optional[int] = Field(0)
    during: Optional[int] = Field(0)
    minPerson: Optional[int] = Field(0)
    maxPerson: Optional[int] = Field(0)
    level: Optional[float] = Field(0.0)
    lockingRatio: Optional[int] = Field(0)
    detailUrl: Optional[str] = Field("")
    reservationUrl: Optional[str] = Field("")


class UpdateThemeDto(BaseModel):
    cafeId: str
    name: str
    intro: str
    thumbnail: Optional[str] = Field("")
    genre: Optional[str] = Field("")
    price: Optional[int] = Field(0)
    during: Optional[int] = Field(0)
    minPerson: Optional[int] = Field(0)
    maxPerson: Optional[int] = Field(0)
    level: Optional[float] = Field(0.0)
    lockingRatio: Optional[int] = Field(0)
    detailUrl: Optional[str] = Field("")
    reservationUrl: Optional[str] = Field("")
    status: str
