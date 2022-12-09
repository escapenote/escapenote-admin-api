import uuid
import boto3
from fastapi import APIRouter, File, UploadFile


router = APIRouter(
    prefix="/images",
    tags=["images"],
    responses={404: {"description": "Not found"}},
)


@router.post("")
async def upload_image(folderName: str, file: UploadFile = File(None)):
    """
    이미지 업로드
    """
    session = boto3.Session()
    s3 = session.resource("s3")
    bucket_name = "escapenote-images"
    bucket = s3.Bucket(bucket_name)

    try:
        filename = uuid.uuid1()
        type = "jpeg"
        key = f"{folderName}/{filename}.{type}"
        bucket.upload_fileobj(
            file.file,
            key,
            ExtraArgs={
                "ContentType": f"image/{type}",
                "CacheControl": "max-age=172800",
            },
        )
        return {"url": f"/{key}"}
    except Exception as e:
        print("error", e)
        return None


@router.delete("")
async def remove_image(key: str):
    """
    이미지 삭제
    """
    session = boto3.Session()
    s3 = session.resource("s3")
    bucket_name = "escapenote-images"
    bucket = s3.Bucket(bucket_name)
    key = key[1:]

    try:
        bucket.delete_objects(Delete={"Objects": [{"Key": key}]})
    except Exception as e:
        print("error", e)
        return None
