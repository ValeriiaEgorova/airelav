import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from database import get_session
from models import APIKey, User

SECRET_KEY = os.getenv("SECRET_KEY", "")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in .env file")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") or ""
        if not email:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_optional(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
    session: Session = Depends(get_session),
) -> User | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            return None
        user = session.exec(select(User).where(User.email == email)).first()
        return user
    except JWTError:
        return None


async def get_user_by_api_key(
    api_key_header: str = Depends(
        OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
    ),
    session: Session = Depends(get_session),
) -> User | None:
    if not api_key_header:
        return None

    api_key_obj = session.exec(
        select(APIKey).where(APIKey.key == api_key_header)
    ).first()

    if api_key_obj and api_key_obj.is_active:
        return api_key_obj.user
    return None


async def get_current_user_or_api_key(
    jwt_user: User | None = Depends(get_current_user_optional),
    api_key_user: User | None = Depends(get_user_by_api_key),
) -> User:
    if jwt_user:
        return jwt_user
    if api_key_user:
        return api_key_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials (JWT or API Key required)",
    )
