from pydantic import BaseModel
from fastapi_cloudauth.cognito import Cognito

from app.config import settings

auth = Cognito(
    region=settings.aws_region,
    userPoolId=settings.aws_user_pool_id,
    client_id=settings.aws_app_client_id,
)


class AccessUser(BaseModel):
    sub: str
