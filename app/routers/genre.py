from typing import Optional
from fastapi import APIRouter

from app.prisma import prisma
from app.models.genre import GenreListRes


router = APIRouter(
    prefix="/genre",
    tags=["genre"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=GenreListRes)
async def get_genre_list(
    skip: Optional[int] = 0,
    take: Optional[int] = 20,
    sort: Optional[str] = "id",
    order: Optional[str] = "asc",
):
    """
    장르 리스트
    """
    total = await prisma.genre.count()
    genre_list = await prisma.genre.find_many(
        skip=skip,
        take=take,
        order={sort: order},
    )
    return {"total": total, "items": genre_list}
