from typing import Optional
from fastapi import APIRouter

from app.prisma import prisma
from app.models.genre import CreateGenreDto, GenreListRes


router = APIRouter(
    prefix="/genre",
    tags=["genre"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=GenreListRes)
async def get_genre_list(
    term: Optional[str] = None,
    includeThemes: Optional[bool] = False,
    skip: Optional[int] = 0,
    take: Optional[int] = 20,
    sort: Optional[str] = "id",
    order: Optional[str] = "asc",
):
    """
    장르 리스트
    """
    where = dict()
    if term:
        where["id"] = {"contains": term}

    options = {
        "skip": skip,
        "take": take,
        "where": where,
        "include": {"themes": includeThemes},
        "order": {sort: order},
    }

    total = await prisma.genre.count(where=where)
    genre_list = await prisma.genre.find_many(**options)
    return {"total": total, "items": genre_list}


@router.post("")
async def create_genre(body: CreateGenreDto):
    """
    장르 추가
    """
    genre = await prisma.genre.create(
        data={
            "id": body.id,
        }
    )
    return genre


@router.delete("/{id}")
async def delete_genre(id: str):
    """
    장르 삭제
    """
    await prisma.genre.delete(
        where={"id": id},
    )
