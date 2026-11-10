from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from app.core.security import decode_access_token
from app.db import get_database
from app.repositories import UserRepository


bearer = HTTPBearer(auto_error=False)


async def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db=Depends(get_database)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        user_id = decode_access_token(credentials.credentials)
        user = await UserRepository(db).by_id(user_id)
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not user: raise HTTPException(status_code=401, detail="User no longer exists")
    return user

