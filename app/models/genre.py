from typing import List, Optional
from pydantic import BaseModel
from prisma import models


class Genre(models.Genre, warn_subclass=False):
    themes: Optional[List["Theme"]]


class GenreListRes(BaseModel):
    total: int
    items: List[Genre]


# For circular dependency
from app.models.theme import Theme

Genre.update_forward_refs()
