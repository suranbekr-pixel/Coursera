from fastapi import APIRouter, HTTPException, Depends, Body, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime
from typing import Optional
from jose import jwt, JWTError

from mysite.database.models import User, RefreshToken, RoleChoices
from mysite.database.schema import (
    UserRegisterSchema,
    UserLoginSchema,
    CurrentUserSchema,
    UserOutputSchema
)
from mysite.database.db import SessionLocal
from mysite.config import (
    SECRET_KEY, ALGORITHM,
    ACCESS_TOKEN_LIFETIME_DAYS, REFRESH_TOKEN_LIFETIME_DAYS
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/login/')

auth_router = APIRouter(prefix='/auth', tags=['Authorization'])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


credentials_exception = HTTPException(
    status_code=401,
    detail='Access token туура эмес же мөөнөтү бүттү',
    headers={'WWW-Authenticate': 'Bearer'},
)


async def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get('sub')
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise credentials_exception

    return user_db


async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Токен жок болсо None кайтарат, токен бар болсо колдонуучуну таап берет"""
    if not authorization:
        return None
    try:
        parts = authorization.strip().split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        token = parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get('sub')
        if subject is None:
            return None
        user_id = int(subject)
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Токен 7 күнгө чейин активдүү болот (30 мүнөттө өчүп калбайт)
    expires = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=ACCESS_TOKEN_LIFETIME_DAYS))
    to_encode.update({'exp': expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS))


def get_token_data(user: User):
    return {
        'sub': str(user.id),
        'email': user.email,
        'role': user.role.value if hasattr(user.role, 'value') else str(user.role)
    }


@auth_router.post('/register/', response_model=dict)
@auth_router.post('/register', response_model=dict, include_in_schema=False)
async def register(user: UserRegisterSchema, db: Session = Depends(get_db)):
    email_db = db.query(User).filter(User.email == user.email).first()
    if email_db:
        raise HTTPException(detail='Бул email катталган', status_code=400)

    hash_password = get_password_hash(user.password)
    user_data = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password,
        role=user.role,
        user_status=user.user_status,
        is_active=user.is_active
    )
    db.add(user_data)
    db.commit()
    db.refresh(user_data)

    # Регистрация болгондо дароо 7 күндүк токен чыгарып беребиз
    token_data = get_token_data(user_data)
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    token_db = RefreshToken(user_id=user_data.id, token=refresh_token)
    db.add(token_db)
    db.commit()

    return {
        'message': 'Сиз ийгиликтүү регистрация болдуңуз',
        'user_id': user_data.id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }


@auth_router.post('/login/', response_model=dict)
@auth_router.post('/login', response_model=dict, include_in_schema=False)
async def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == user.email).first()
    if not user_db or not verify_password(user.password, user_db.password):
        raise HTTPException(detail='Сиз жазган маалымат туура эмес', status_code=401)

    token_data = get_token_data(user_db)

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    token_db = RefreshToken(user_id=user_db.id, token=refresh_token)
    db.add(token_db)
    db.commit()

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'user': CurrentUserSchema.from_orm(user_db)
    }


@auth_router.post('/refresh/', response_model=dict)
@auth_router.post('/refresh', response_model=dict, include_in_schema=False)
async def refresh(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Маалымат туура эмес')

    user_db = stored_token.token_user
    token_data = get_token_data(user_db)

    access_token = create_access_token(token_data)
    return {'access_token': access_token, 'token_type': 'Bearer'}


@auth_router.post('/logout/', response_model=dict)
@auth_router.post('/logout', response_model=dict, include_in_schema=False)
async def logout(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Маалымат туура эмес')

    db.delete(stored_token)
    db.commit()

    return {'message': 'Ийгиликтүү чыгып кеттиңиз'}


@auth_router.get('/verify/', response_model=CurrentUserSchema)
@auth_router.get('/verify', response_model=CurrentUserSchema, include_in_schema=False)
async def verify_access_token(current_user: User = Depends(get_current_user)):
    return current_user


@auth_router.get('/me/', response_model=UserOutputSchema)
@auth_router.get('/me', response_model=UserOutputSchema, include_in_schema=False)
async def user_me(current_user: User = Depends(get_current_user)):
    return current_user
