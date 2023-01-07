import boto3
import json
import requests
from bs4 import BeautifulSoup
from typing import Optional
from fastapi import APIRouter, HTTPException

from app.prisma import prisma
from app.config import settings
from app.models.cafe import CafeListRes, CafeDetailRes, CreateCafeDto, UpdateCafeDto
from app.utils.image import upload_image


router = APIRouter(
    prefix="/cafes",
    tags=["cafes"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=CafeListRes)
async def get_cafes(
    term: Optional[str] = None,
    areaA: Optional[str] = None,
    areaB: Optional[str] = None,
    status: Optional[str] = None,
    skip: Optional[int] = 0,
    take: Optional[int] = 20,
    sort: Optional[str] = "createdAt",
    order: Optional[str] = "desc",
):
    where = dict()
    if term:
        where["name"] = {"contains": term}
    if areaA:
        where["areaA"] = areaA
    if areaB:
        where["areaB"] = areaB
    if status:
        where["status"] = status

    options = {
        "skip": skip,
        "take": take,
        "where": where,
        "include": {"themes": True},
        "order": {sort: order},
    }

    total = await prisma.cafe.count(where=where)
    cafes = await prisma.cafe.find_many(**options)
    return {"total": total, "items": cafes}


@router.get("/{id}", response_model=CafeDetailRes)
async def get_cafe(id: str):
    cafe = await prisma.cafe.find_unique(
        where={"id": id},
        include={"themes": True},
    )
    return cafe


@router.post("")
async def create_cafe(body: CreateCafeDto):
    """
    카페 추가
    """
    images = list()
    for i in range(len(body.images)):
        if "http" in body.images[i]:
            url = upload_image(body.images[i], "cafes")
        else:
            url = body.images[i]

        if url:
            images.append(url)

    cafe = await prisma.cafe.create(
        data={
            "naverMapId": body.naverMapId,
            "areaA": body.areaA,
            "areaB": body.areaB,
            "name": body.name,
            "intro": body.intro,
            "addressLine": body.addressLine,
            "lat": body.lat,
            "lng": body.lng,
            "images": json.dumps(images),
            "website": body.website,
            "tel": body.tel,
            "openingHours": body.openingHours,
            "status": "PUBLISHED",
        }
    )
    return cafe


@router.patch("/{id}")
async def update_cafe(id: str, body: UpdateCafeDto):
    """
    카페 수정
    """
    images = list()
    for i in range(len(body.images)):
        if "http" in body.images[i]:
            url = upload_image(body.images[i], "cafes")
        else:
            url = body.images[i]

        if url:
            images.append(url)

    cafe = await prisma.cafe.update(
        where={"id": id},
        data={
            "naverMapId": body.naverMapId,
            "areaA": body.areaA,
            "areaB": body.areaB,
            "name": body.name,
            "intro": body.intro,
            "addressLine": body.addressLine,
            "lat": body.lat,
            "lng": body.lng,
            "images": json.dumps(images),
            "website": body.website,
            "tel": body.tel,
            "openingHours": body.openingHours,
            "status": body.status,
        },
    )
    return cafe


@router.patch("/{id}/enabled")
async def enabled_cafe(id: str):
    """
    카페 활성화
    """
    await prisma.cafe.update(
        where={"id": id},
        data={"status": "PUBLISHED"},
    )


@router.patch("/{id}/disabled")
async def disabled_cafe(id: str):
    """
    카페 비활성화
    """
    await prisma.cafe.update(
        where={"id": id},
        data={"status": "DELETED"},
    )


@router.delete("/{id}")
async def delete_cafe(id: str):
    """
    카페 삭제
    """
    session = boto3.Session()
    s3 = session.resource("s3")
    bucket_name = settings.bucket_name
    bucket = s3.Bucket(bucket_name)

    # 테마 이미지 및 데이터 삭제
    themes = await prisma.theme.find_many(where={"cafeId": id})
    for theme in themes:
        if theme.thumbnail:
            bucket.delete_objects(Delete={"Objects": [{"Key": theme.thumbnail[1:]}]})
    await prisma.theme.delete_many(where={"cafeId": id})

    # 카페 이미지 및 데이터 삭제
    cafe = await prisma.cafe.find_unique(where={"id": id})
    for image in cafe.images:
        bucket.delete_objects(Delete={"Objects": [{"Key": image[1:]}]})
    await prisma.cafe.delete(where={"id": id})


@router.get("/{naver_map_id}/cafe")
async def get_cafe_by_naver_map_id(naver_map_id: str):
    """
    네이버 장소 아이디로 카페 상세 조회
    """
    cafe = await prisma.cafe.find_first(
        where={"naverMapId": naver_map_id},
    )
    return cafe


@router.get("/{naver_map_id}/map")
async def get_place_info(naver_map_id: str):
    """
    네이버 장소 정보 가져오기
    """
    res = requests.get(
        f"https://m.place.naver.com/place/{naver_map_id}/home",
    )
    soup = BeautifulSoup(res.content, "lxml")

    try:
        text = soup.find_all("script")[2].text
        p1 = str(text).split("window.__APOLLO_STATE__ = ")[1]
        p2 = p1.split("window.__LOCATION_STATE__ = ")[0]
        p3 = p2.split("window.__PLACE_STATE__ = ")

        apollo_state = p3[0].replace(";", "")
        item = json.loads(apollo_state)
        id = f"PlaceBase:{naver_map_id}"

        name = item[id]["name"]
        intro = item[id]["description"]
        website = item[id]["homepages"]["repr"]["url"]
        tel = item[id]["phone"]
        newBusinessHours = item["ROOT_QUERY"][
            'place({"deviceType":"mobile","id":'
            + f'"{naver_map_id}"'
            + ',"isNx":false})'
        ]["newBusinessHours"]
        if newBusinessHours:
            openingHoursData = newBusinessHours[0]["businessHours"]
            if openingHoursData:
                description = openingHoursData[0]["description"]
                if description == "휴무":
                    openingHours = [
                        {"day": "월", "openTime": "", "closeTime": ""},
                        {"day": "화", "openTime": "", "closeTime": ""},
                        {"day": "수", "openTime": "", "closeTime": ""},
                        {"day": "목", "openTime": "", "closeTime": ""},
                        {"day": "금", "openTime": "", "closeTime": ""},
                        {"day": "토", "openTime": "", "closeTime": ""},
                        {"day": "일", "openTime": "", "closeTime": ""},
                    ]
                else:
                    formattedOpeningHours = list(
                        map(
                            lambda x: {
                                "day": x["day"],
                                "openTime": x["businessHours"]["start"],
                                "closeTime": x["businessHours"]["end"],
                            },
                            openingHoursData,
                        )
                    )
                    day = formattedOpeningHours[0]["day"]
                    if "매일" in day:
                        open_itme = formattedOpeningHours[0]["openTime"]
                        close_itme = formattedOpeningHours[0]["closeTime"]
                        openingHours = [
                            {
                                "day": "월",
                                "openTime": open_itme,
                                "closeTime": close_itme,
                            },
                            {
                                "day": "화",
                                "openTime": open_itme,
                                "closeTime": close_itme,
                            },
                            {
                                "day": "수",
                                "openTime": open_itme,
                                "closeTime": close_itme,
                            },
                            {
                                "day": "목",
                                "openTime": open_itme,
                                "closeTime": close_itme,
                            },
                            {
                                "day": "금",
                                "openTime": open_itme,
                                "closeTime": close_itme,
                            },
                            {
                                "day": "토",
                                "openTime": open_itme,
                                "closeTime": close_itme,
                            },
                            {
                                "day": "일",
                                "openTime": open_itme,
                                "closeTime": close_itme,
                            },
                        ]
                    else:
                        order = {"월": 1, "화": 2, "수": 3, "목": 4, "금": 5, "토": 6, "일": 7}
                        openingHours = sorted(
                            formattedOpeningHours, key=lambda d: order[d["day"]]
                        )
        else:
            openingHours = [
                {"day": "월", "openTime": "", "closeTime": ""},
                {"day": "화", "openTime": "", "closeTime": ""},
                {"day": "수", "openTime": "", "closeTime": ""},
                {"day": "목", "openTime": "", "closeTime": ""},
                {"day": "금", "openTime": "", "closeTime": ""},
                {"day": "토", "openTime": "", "closeTime": ""},
                {"day": "일", "openTime": "", "closeTime": ""},
            ]
        images = list(map(lambda x: x["origin"], item[id]["images"]))
        addressLine = item[id]["roadAddress"]
        areaA = str(addressLine).split(" ")[0]
        areaB = str(addressLine).split(" ")[1]
        coordinate = item[id]["coordinate"]

        return {
            "name": name,
            "intro": intro,
            "website": website,
            "tel": tel,
            "openingHours": openingHours,
            "images": images,
            "areaA": areaA,
            "areaB": areaB,
            "addressLine": addressLine,
            "lat": coordinate["y"],
            "lng": coordinate["x"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
