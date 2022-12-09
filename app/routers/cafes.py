import json
from typing import Optional
from fastapi import APIRouter

from app.prisma import prisma
from app.models.cafe import CafeListRes, CafeDetailRes, CreateCafeDto, UpdateCafeDto


router = APIRouter(
    prefix="/cafes",
    tags=["cafes"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=CafeListRes)
async def get_cafes(
    term: Optional[str] = None,
    status: Optional[str] = None,
    skip: Optional[int] = 0,
    take: Optional[int] = 20,
    sort: Optional[str] = "createdAt",
    order: Optional[str] = "desc",
):
    where = dict()
    if term:
        where["name"] = {"contains": term}
    if status:
        where["status"] = status

    options = {
        "skip": skip,
        "take": take,
        "where": where,
        "order": {sort: order},
    }

    total = await prisma.cafe.count()
    cafes = await prisma.cafe.find_many(**options)
    return {"total": total, "items": cafes}


@router.get("/{id}", response_model=CafeDetailRes)
async def get_cafe(id: str):
    cafe = await prisma.cafe.find_unique(where={"id": id})
    return cafe


@router.post("")
async def create_cafe(body: CreateCafeDto):
    """
    카페 추가
    """
    cafe = await prisma.cafe.create(
        data={
            "areaA": body.areaA,
            "areaB": body.areaB,
            "name": body.name,
            "addressLine": body.addressLine,
            "lat": body.lat,
            "lng": body.lng,
            "images": json.dumps(body.images),
            "website": body.website,
            "tel": body.tel,
            "openingHour": body.openingHour,
            "closingHour": body.closingHour,
            "status": "PUBLISHED",
        }
    )
    return cafe


@router.patch("/{id}")
async def update_cafe(id: str, body: UpdateCafeDto):
    """
    카페 수정
    """
    cafe = await prisma.cafe.update(
        where={"id": id},
        data={
            "areaA": body.areaA,
            "areaB": body.areaB,
            "name": body.name,
            "addressLine": body.addressLine,
            "lat": body.lat,
            "lng": body.lng,
            "images": json.dumps(body.images),
            "website": body.website,
            "tel": body.tel,
            "openingHour": body.openingHour,
            "closingHour": body.closingHour,
            "status": body.status,
        },
    )
    return cafe


@router.delete("/{id}")
async def delete_cafe(id: str):
    """
    카페 삭제
    """
    await prisma.cafe.update(
        where={"id": id},
        data={"status": "DELETED"},
    )
