from fastapi import Depends, Request

from app.auth import auth, AccessUser

### 미들웨어에서 사용자 정보를 공유해서 사용하기 위한 용도
async def pass_access_user(
    request: Request, user: AccessUser = Depends(auth.claim(AccessUser))
):
    if user:
        request.state.sub = user.sub
