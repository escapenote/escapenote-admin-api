import json
import requests
from bs4 import BeautifulSoup
from typing import Optional
from fastapi import APIRouter
from fastapi import APIRouter, Depends

from app.dependencies import pass_access_user
from app.prisma import prisma
from app.models.scrapper import (
    CreateScrapperDto,
    UpdateScrapperDto,
)


router = APIRouter(
    prefix="/scrappers",
    tags=["scrappers"],
    responses={404: {"description": "Not found"}},
)


@router.get("", dependencies=[Depends(pass_access_user)])
async def get_scrapper_list(
    status: Optional[str] = None,
    skip: Optional[int] = 0,
    take: Optional[int] = 20,
    sort: Optional[str] = "createdAt",
    order: Optional[str] = "desc",
):
    """
    스크래퍼 리스트
    """
    where = dict()
    if status:
        where["status"] = status

    options = {
        "skip": skip,
        "take": take,
        "where": where,
        "include": {"cafe": True},
        "order": {sort: order},
    }

    total = await prisma.scrapper.count(where=where)
    scrapper_list = await prisma.scrapper.find_many(**options)
    return {"total": total, "items": scrapper_list}


@router.get("/{id}", dependencies=[Depends(pass_access_user)])
async def get_scrapper(id: str):
    """
    스크래퍼 상세 조회
    """
    scrapper = await prisma.scrapper.find_unique(
        where={"id": id},
        include={
            "cafe": True,
            "metric": True,
        },
    )
    return scrapper


@router.post("")
async def create_scrapper(body: CreateScrapperDto):
    """
    스크래퍼 추가
    """
    scrapper = await prisma.scrapper.create(
        data={
            "url": body.url,
            "groupSelector": body.groupSelector,
            "themeSelector": body.themeSelector,
            "branchSelector": body.branchSelector,
            "status": "PUBLISHED",
        }
    )
    return scrapper


@router.patch("/{id}", dependencies=[Depends(pass_access_user)])
async def update_scrapper(id: str, body: UpdateScrapperDto):
    """
    스크래퍼 수정
    """
    scrapper = await prisma.scrapper.update(
        where={"id": id},
        data={
            "cafe": {
                "connect": {"id": body.cafeId},
            },
            "url": body.url,
            "comment": body.comment,
            "groupSelector": body.groupSelector,
            "themeSelector": body.themeSelector,
            "branchSelector": body.branchSelector,
        },
    )
    return scrapper


@router.patch("/{id}/enabled", dependencies=[Depends(pass_access_user)])
async def enabled_scrapper(id: str):
    """
    스크래퍼 활성화
    """
    await prisma.scrapper.update(
        where={"id": id},
        data={"status": "PUBLISHED"},
    )


@router.patch("/{id}/disabled", dependencies=[Depends(pass_access_user)])
async def disabled_scrapper(id: str):
    """
    스크래퍼 비활성화
    """
    await prisma.scrapper.update(
        where={"id": id},
        data={"status": "DELETED"},
    )


@router.delete("/{id}", dependencies=[Depends(pass_access_user)])
async def delete_scrapper(id: str):
    """
    스크래퍼 삭제
    """
    await prisma.scrapper.delete(
        where={"id": id},
    )


@router.get("/{id}/scrap", dependencies=[Depends(pass_access_user)])
async def get_scrapper(id: str):
    """
    스크래퍼 데이터를 이용하여 스크랩 시도
    """
    scrapper = await prisma.scrapper.find_unique(
        where={"id": id},
        include={"metric": True},
    )

    res = requests.get(scrapper.url)
    soup = BeautifulSoup(res.content, "lxml")

    scrapped_theme_els = soup.select(scrapper.themeSelector)
    scrapped_theme_names = list(map(lambda e: str(e.text).strip(), scrapped_theme_els))
    scrapped_theme_names.sort()

    themes = await prisma.theme.find_many(where={"cafeId": scrapper.cafeId})
    current_theme_names = list(map(lambda x: x.name, themes))
    current_theme_names.sort()

    different_theme_names = list()
    for current_theme_name in current_theme_names:
        if current_theme_name not in scrapped_theme_names:
            different_theme_names.append(current_theme_name)
    for scrapped_theme_name in scrapped_theme_names:
        if scrapped_theme_name not in current_theme_names:
            different_theme_names.append(scrapped_theme_name)
    different_theme_names = list(set(different_theme_names))
    different_theme_names.sort()

    data = {
        "scrapper": {"connect": {"id": id}},
        "currentThemes": json.dumps(current_theme_names),
        "scrappedThemes": json.dumps(scrapped_theme_names),
        "differentThemes": json.dumps(different_theme_names),
        "status": "SOMETHING_WRONG" if different_theme_names else "NOTHING_WRONG",
    }

    if scrapper.metric:
        await prisma.metric.update(
            where={"id": scrapper.metric.id},
            data=data,
        )
    else:
        await prisma.metric.create(
            data=data,
        )
