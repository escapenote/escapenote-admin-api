from typing import Optional
from fastapi import APIRouter

from app.prisma import prisma
from app.models.theme import (
    ThemeListRes,
    ThemeDetailRes,
    CreateThemeDto,
    UpdateThemeDto,
)


router = APIRouter(
    prefix="/themes",
    tags=["themes"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=ThemeListRes)
async def get_themes(
    cafeId: Optional[str] = None,
    term: Optional[str] = None,
    status: Optional[str] = None,
    skip: Optional[int] = 0,
    take: Optional[int] = 20,
    sort: Optional[str] = "createdAt",
    order: Optional[str] = "desc",
):
    """
    테마 리스트
    """
    where = dict()
    if cafeId:
        where["cafeId"] = cafeId
    if term:
        where["name"] = {"contains": term}
    if status:
        where["status"] = status

    options = {
        "skip": skip,
        "take": take,
        "where": where,
        "include": {"cafe": True},
        "order": {sort: order},
    }

    total = await prisma.theme.count(where=where)
    themes = await prisma.theme.find_many(**options)
    return {"total": total, "items": themes}


@router.get("/{id}", response_model=ThemeDetailRes)
async def get_theme(id: str):
    """
    테마 상세
    """
    theme = await prisma.theme.find_unique(where={"id": id})
    return theme


@router.post("")
async def create_theme(body: CreateThemeDto):
    """
    테마 추가
    """
    theme = await prisma.theme.create(
        data={
            "cafeId": body.cafeId,
            "name": body.name,
            "intro": body.intro,
            "thumbnail": body.thumbnail,
            "genre": body.genre,
            "price": body.price,
            "during": body.during,
            "minPerson": body.minPerson,
            "maxPerson": body.maxPerson,
            "level": body.level,
            "lockingRatio": body.lockingRatio,
            "fear": body.fear,
            "openDate": body.openDate,
            "detailUrl": body.detailUrl,
            "reservationUrl": body.reservationUrl,
            "status": "PUBLISHED",
        }
    )
    return theme


@router.patch("/{id}")
async def update_theme(id: str, body: UpdateThemeDto):
    """
    테마 수정
    """
    theme = await prisma.theme.update(
        where={"id": id},
        data={
            "cafeId": body.cafeId,
            "name": body.name,
            "intro": body.intro,
            "thumbnail": body.thumbnail,
            "genre": body.genre,
            "price": body.price,
            "during": body.during,
            "minPerson": body.minPerson,
            "maxPerson": body.maxPerson,
            "level": body.level,
            "lockingRatio": body.lockingRatio,
            "fear": body.fear,
            "openDate": body.openDate,
            "detailUrl": body.detailUrl,
            "reservationUrl": body.reservationUrl,
            "status": body.status,
        },
    )
    return theme


@router.delete("/{id}")
async def delete_theme(id: str):
    """
    테마 삭제
    """
    await prisma.theme.update(
        where={"id": id},
        data={"status": "DELETED"},
    )
