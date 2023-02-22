import boto3
from typing import Optional
from fastapi import APIRouter

from app.prisma import prisma
from app.config import settings
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
        where["displayName"] = {"contains": term}
    if status:
        where["status"] = status

    options = {
        "skip": skip,
        "take": take,
        "where": where,
        "include": {
            "cafe": True,
            "genre": True,
        },
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
    theme = await prisma.theme.find_unique(
        where={"id": id},
        include={"genre": True},
    )
    return theme


@router.post("")
async def create_theme(body: CreateThemeDto):
    """
    테마 추가
    """
    genre = list(map(lambda x: {"id": x}, body.genre))
    theme = await prisma.theme.create(
        data={
            "cafeId": body.cafeId,
            "name": body.name,
            "displayName": body.displayName,
            "intro": body.intro,
            "thumbnail": body.thumbnail,
            "genre": {
                "connect": genre,
            },
            "price": body.price,
            "during": body.during,
            "minPerson": body.minPerson,
            "maxPerson": body.maxPerson,
            "level": body.level,
            "lockingRatio": body.lockingRatio,
            "fear": body.fear,
            "activity": body.activity,
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
    genre = list(map(lambda x: {"id": x}, body.genre))
    # 장르 초기화
    await prisma.theme.update(
        where={"id": id},
        data={"genre": {"set": []}},
    )
    theme = await prisma.theme.update(
        where={"id": id},
        data={
            "cafeId": body.cafeId,
            "name": body.name,
            "displayName": body.displayName,
            "intro": body.intro,
            "thumbnail": body.thumbnail,
            "genre": {
                "connect": genre,
            },
            "price": body.price,
            "during": body.during,
            "minPerson": body.minPerson,
            "maxPerson": body.maxPerson,
            "level": body.level,
            "lockingRatio": body.lockingRatio,
            "fear": body.fear,
            "activity": body.activity,
            "openDate": body.openDate,
            "detailUrl": body.detailUrl,
            "reservationUrl": body.reservationUrl,
            "status": body.status,
        },
    )
    return theme


@router.patch("/{id}/enabled")
async def enabled_theme(id: str):
    """
    테마 활성화
    """
    await prisma.theme.update(
        where={"id": id},
        data={"status": "PUBLISHED"},
    )


@router.patch("/{id}/disabled")
async def disabled_theme(id: str):
    """
    테마 비활성화
    """
    await prisma.theme.update(
        where={"id": id},
        data={"status": "DELETED"},
    )


@router.delete("/{id}")
async def delete_theme(id: str):
    """
    테마 삭제
    """
    session = boto3.Session()
    s3 = session.resource("s3")
    bucket_name = settings.bucket_name
    bucket = s3.Bucket(bucket_name)

    # 테마 이미지 및 데이터 삭제
    theme = await prisma.theme.find_unique(where={"id": id})
    if theme.thumbnail:
        bucket.delete_objects(Delete={"Objects": [{"Key": theme.thumbnail[1:]}]})
    await prisma.theme.delete(where={"id": id})
