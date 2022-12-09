from typing import Any, List, Optional
from pydantic import BaseModel, Field
from prisma import models


class Cafe(models.Cafe, warn_subclass=False):
    images: List[str]


class CafeListRes(BaseModel):
    total: int
    items: List[Cafe]


class CafeDetailRes(BaseModel):
    class _Cafe(Cafe, warn_subclass=False):
        themesCount: int

    __root__: _Cafe


class CreateCafeDto(BaseModel):
    areaA: str
    areaB: str
    name: str
    addressLine: Optional[str] = Field("")
    lat: Optional[float] = Field(0.0)
    lng: Optional[float] = Field(0.0)
    images: Optional[Any] = Field("[]")
    website: Optional[str] = Field("")
    tel: Optional[str] = Field("")
    openingHour: Optional[int] = Field(0)
    closingHour: Optional[int] = Field(0)
    since: Optional[str] = Field("")


class UpdateCafeDto(BaseModel):
    areaA: str
    areaB: str
    name: str
    addressLine: Optional[str] = Field("")
    lat: Optional[float] = Field(0.0)
    lng: Optional[float] = Field(0.0)
    images: Optional[Any] = Field("[]")
    website: Optional[str] = Field("")
    tel: Optional[str] = Field("")
    openingHour: Optional[int] = Field(0)
    closingHour: Optional[int] = Field(0)
    since: Optional[str] = Field("")
    status: str
