from typing import Optional
from fastapi import APIRouter, BackgroundTasks

from app.prisma import prisma
from app.utils.scrapper import scrap_all_themes


router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_metrics(
    status: Optional[str] = None,
    skip: Optional[int] = 0,
    take: Optional[int] = 20,
    sort: Optional[str] = "createdAt",
    order: Optional[str] = "desc",
):
    """
    지표 조회
    """
    where = dict()
    if status:
        where["status"] = status

    options = {
        "skip": skip,
        "take": take,
        "where": where,
        "include": {
            "scrapper": {
                "include": {
                    "cafe": True,
                },
            }
        },
        "order": {sort: order},
    }

    total = await prisma.metric.count(where=where)
    metrics = await prisma.metric.find_many(**options)
    return {"total": total, "items": metrics}


@router.get("/{id}")
async def get_metric(id: str):
    """
    메트릭 상세 조회
    """
    metric = await prisma.metric.find_unique(
        where={"id": id},
        include={"scrapper": True},
    )
    return metric


@router.post("")
async def post_metric(background_tasks: BackgroundTasks):
    """
    스크래퍼의 모든 데이터를 이용하여 스크랩
    """
    scrappers = await prisma.scrapper.find_many(
        where={"status": "PUBLISHED", "cafeId": {"not": None}},
    )
    await prisma.metric.delete_many()
    background_tasks.add_task(scrap_all_themes, scrappers=scrappers)
    return True


@router.patch("/{id}/status")
async def change_metric_status(id: str):
    """
    메트릭 이상없음으로 상태 변경
    """
    await prisma.metric.update(
        where={"id": id},
        data={"status": "NOTHING_WRONG"},
    )
