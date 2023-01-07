import uuid
import boto3
import requests
import mimetypes

from app.config import settings


def upload_image(image_url: str, folder_name: str):
    """
    이미지 URL을 s3에 다이렉트로 저장
    """
    try:
        r = requests.get(image_url, stream=True)

        session = boto3.Session()
        s3 = session.resource("s3")
        bucket_name = settings.bucket_name
        file_name = uuid.uuid1()

        content_type = r.headers["content-type"]
        if "application" in content_type:
            return ""
        ext = mimetypes.guess_extension(content_type).replace(".", "")
        key = f"{folder_name}/{file_name}.{ext}"

        bucket = s3.Bucket(bucket_name)
        bucket.upload_fileobj(
            r.raw,
            key,
            ExtraArgs={
                "ContentType": content_type,
                "CacheControl": "max-age=172800",
            },
        )
        return f"/{key}"
    except:
        return ""
