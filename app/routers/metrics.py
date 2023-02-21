import json
import requests
from bs4 import BeautifulSoup
from typing import Optional
from fastapi import APIRouter

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from app.prisma import prisma


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
async def post_metric():
    """
    스크래퍼의 모든 데이터를 이용하여 스크랩
    """
    scrappers = await prisma.scrapper.find_many(
        where={"status": "PUBLISHED", "cafeId": {"not": None}},
    )

    result = list()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service("app/chromedriver"), options=options)
    wait = WebDriverWait(driver, 10)

    for scrapper in scrappers:
        driver.get(scrapper.url)

        # XPath
        if scrapper.themeSelector and scrapper.themeSelector[0] == "/":
            wait.until(presence_of_element_located((By.XPATH, scrapper.themeSelector)))
            scrapped_theme_els = driver.find_elements(By.XPATH, scrapper.themeSelector)
        # CSS
        else:
            wait.until(
                presence_of_element_located((By.CSS_SELECTOR, scrapper.themeSelector))
            )
            scrapped_theme_els = driver.find_elements(
                By.CSS_SELECTOR, scrapper.themeSelector
            )
        scrapped_theme_names = list(
            map(lambda e: str(e.text).strip(), scrapped_theme_els)
        )
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

        result.append(
            {
                "scrapperId": scrapper.id,
                "currentThemes": json.dumps(current_theme_names),
                "scrappedThemes": json.dumps(scrapped_theme_names),
                "differentThemes": json.dumps(different_theme_names),
                "status": "SOMETHING_WRONG"
                if different_theme_names
                else "NOTHING_WRONG",
            }
        )

    driver.close()

    await prisma.metric.delete_many()
    await prisma.metric.create_many(data=result)

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
