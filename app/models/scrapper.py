from typing import List, Optional
from pydantic import BaseModel, Field
from prisma import models


class Scrapper(models.Scrapper, warn_subclass=False):
    cafe: Optional["Cafe"]


class CreateScrapperDto(BaseModel):
    url: str
    groupSelector: Optional[str] = Field("")
    themeSelector: str
    branchSelector: Optional[str] = Field("")


class UpdateScrapperDto(BaseModel):
    cafeId: str
    url: str
    comment: Optional[str] = Field("")
    groupSelector: Optional[str] = Field("")
    themeSelector: str
    branchSelector: Optional[str] = Field("")


# For circular dependency
from app.models.cafe import Cafe

Scrapper.update_forward_refs()
