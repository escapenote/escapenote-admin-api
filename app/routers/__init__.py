from fastapi import APIRouter, Depends

from app.dependencies import pass_access_user
from app.routers import cafes
from app.routers import genre
from app.routers import themes
from app.routers import images

routers = APIRouter()

routers.include_router(cafes.router, dependencies=[Depends(pass_access_user)])
routers.include_router(genre.router, dependencies=[Depends(pass_access_user)])
routers.include_router(themes.router, dependencies=[Depends(pass_access_user)])
routers.include_router(images.router, dependencies=[Depends(pass_access_user)])
