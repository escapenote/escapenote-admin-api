from typing import Any, List, Optional
from pydantic import BaseModel, Field
from prisma import models


class Cafe(models.Cafe, warn_subclass=False):
    images: Optional[List[str]]
    openingHours: Optional[List["OpeningHours"]]


class OpeningHours(BaseModel):
    day: str
    openTime: str
    closeTime: str


class CafeListRes(BaseModel):
    total: int
    items: List[Cafe]


class CafeDetailRes(BaseModel):
    __root__: Cafe


class CreateCafeDto(BaseModel):
    naverMapId: Optional[str] = Field("")
    areaA: str
    areaB: str
    name: str
    intro: Optional[str] = Field("")
    addressLine: Optional[str] = Field("")
    lat: Optional[float] = Field(0.0)
    lng: Optional[float] = Field(0.0)
    images: Optional[Any] = Field([])
    website: Optional[str] = Field("")
    tel: Optional[str] = Field("")
    openingHours: Optional[Any] = Field("[]")
    closingHour: Optional[int] = Field(0)


class UpdateCafeDto(BaseModel):
    naverMapId: Optional[str] = Field("")
    areaA: str
    areaB: str
    name: str
    intro: Optional[str] = Field("")
    addressLine: Optional[str] = Field("")
    lat: Optional[float] = Field(0.0)
    lng: Optional[float] = Field(0.0)
    images: Optional[Any] = Field([])
    website: Optional[str] = Field("")
    tel: Optional[str] = Field("")
    openingHours: Optional[Any] = Field("[]")
    status: str


# For circular dependency
Cafe.update_forward_refs()
