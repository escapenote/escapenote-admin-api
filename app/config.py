from pydantic import BaseSettings


class Settings(BaseSettings):
    # Common
    app_env: str

    # AWS
    aws_region: str
    aws_user_pool_id: str
    aws_app_client_id: str


settings = Settings()
