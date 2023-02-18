from typing import List, Optional
from pydantic import BaseModel, Field
from prisma import models


class Theme(models.Theme, warn_subclass=False):
    cafe: Optional["Cafe"]


class ThemeListRes(BaseModel):
    total: int
    items: List[Theme]


class ThemeDetailRes(BaseModel):
    __root__: Theme


class CreateThemeDto(BaseModel):
    cafeId: str
    name: str
    displayName: str
    intro: str
    thumbnail: str
    genre: Optional[List[str]] = Field([])
    price: int
    during: int
    minPerson: int
    maxPerson: int
    level: float
    lockingRatio: Optional[int] = Field(0)
    fear: Optional[int] = Field(0)
    activity: Optional[int] = Field(0)
    openDate: Optional[str] = Field("")
    detailUrl: Optional[str] = Field("")
    reservationUrl: Optional[str] = Field("")


class UpdateThemeDto(BaseModel):
    cafeId: str
    name: str
    displayName: str
    intro: str
    thumbnail: str
    genre: Optional[List[str]] = Field([])
    price: int
    during: int
    minPerson: int
    maxPerson: int
    level: float
    lockingRatio: Optional[int] = Field(0)
    fear: Optional[int] = Field(0)
    activity: Optional[int] = Field(0)
    openDate: Optional[str] = Field("")
    detailUrl: Optional[str] = Field("")
    reservationUrl: Optional[str] = Field("")
    status: str


# For circular dependency
from app.models.cafe import Cafe

Theme.update_forward_refs()
