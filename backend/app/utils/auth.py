"""
Supabase Auth 验证中间件
验证前端传来的 Supabase JWT Token
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.config import get_settings

settings = get_settings()
security = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT Token 解析后的数据"""
    sub: str  # user id
    email: Optional[str] = None
    role: Optional[str] = None
    aud: Optional[str] = None
    exp: Optional[int] = None


class CurrentUser(BaseModel):
    """当前登录用户"""
    id: UUID
    email: Optional[str] = None
    role: str = "authenticated"


async def verify_token(token: str) -> TokenPayload:
    """验证 Supabase JWT Token"""
    try:
        # Supabase 使用 HS256 算法
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"  # Supabase 默认 audience
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """获取当前登录用户的依赖"""
    token = credentials.credentials
    payload = await verify_token(token)

    return CurrentUser(
        id=UUID(payload.sub),
        email=payload.email,
        role=payload.role or "authenticated"
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[CurrentUser]:
    """可选的用户验证（允许未登录访问）"""
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = await verify_token(token)
        return CurrentUser(
            id=UUID(payload.sub),
            email=payload.email,
            role=payload.role or "authenticated"
        )
    except HTTPException:
        return None
