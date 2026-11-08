from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from mysite.database.models import User, RoleChoices
from mysite.database.schema import UserOutputSchema, UserRegisterSchema, UserLoginSchema, UserUpdateSchema
from mysite.api.auth import get_db, get_current_user, get_optional_current_user, get_password_hash, register, login

user_router = APIRouter(tags=['User'])


@user_router.get('/', response_model=List[UserOutputSchema], summary='List Users')
@user_router.get('', response_model=List[UserOutputSchema], include_in_schema=False)
async def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@user_router.post('/', response_model=UserOutputSchema, summary='Create User')
@user_router.post('', response_model=UserOutputSchema, include_in_schema=False)
async def create_user_direct(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    """Жаңы колдонуучу түзүү"""
    email_db = db.query(User).filter(User.email == user_data.email).first()
    if email_db:
        return email_db

    hash_password = get_password_hash(user_data.password)
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hash_password,
        role=user_data.role,
        user_status=user_data.user_status,
        is_active=user_data.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@user_router.get('/{user_id}/', response_model=UserOutputSchema, summary='Detail User')
@user_router.get('/{user_id}', response_model=UserOutputSchema, include_in_schema=False)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Колдонуучу табылган жок")
    return user_db


@user_router.put('/{user_id}/', response_model=UserOutputSchema, summary='Update User')
@user_router.put('/{user_id}', response_model=UserOutputSchema, include_in_schema=False)
async def update_user(user_id: int, user_data: UserUpdateSchema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Колдонуучу табылган жок")

    update_dict = user_data.dict(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(user_db, field, val)
    db.commit()
    db.refresh(user_db)
    return user_db


@user_router.delete('/{user_id}/', response_model=dict, summary='Delete User')
@user_router.delete('/{user_id}', response_model=dict, include_in_schema=False)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Колдонуучу табылган жок")
    db.delete(user_db)
    db.commit()
    return {"message": "Колдонуучу ийгиликтүү өчүрүлдү"}


@user_router.post('/register/', response_model=UserOutputSchema, include_in_schema=False)
@user_router.post('/register', response_model=UserOutputSchema, include_in_schema=False)
async def user_register_alias(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    return await create_user_direct(user_data=user_data, db=db)


@user_router.post('/login/', response_model=dict, include_in_schema=False)
@user_router.post('/login', response_model=dict, include_in_schema=False)
async def user_login_alias(user_data: UserLoginSchema, db: Session = Depends(get_db)):
    res = await login(user=user_data, db=db)
    return {
        "access_token": res["access_token"],
        "refresh_token": res["refresh_token"],
        "token_type": "bearer"
    }

