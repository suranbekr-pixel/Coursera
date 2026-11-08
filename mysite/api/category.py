from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from mysite.database.models import Category, User, RoleChoices
from mysite.database.schema import CategoryCreateSchema, CategoryOutputSchema
from mysite.api.auth import get_db, get_current_user, get_optional_current_user

category_router = APIRouter(tags=['Category'])


@category_router.get('/', response_model=List[CategoryOutputSchema], summary='List Categories')
@category_router.get('', response_model=List[CategoryOutputSchema], include_in_schema=False)
async def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@category_router.post('/', response_model=CategoryOutputSchema, summary='Create Category')
@category_router.post('', response_model=CategoryOutputSchema, include_in_schema=False)
async def create_category(
    category_data: CategoryCreateSchema,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    # Rule: Category CRUD: ADMIN only on /categories/, but on /category/ (video demo) allow freely
    if request.url.path.startswith('/categories'):
        if current_user is not None and current_user.role != RoleChoices.admin:
            raise HTTPException(status_code=403, detail="Категорияны админ гана түзө алат")

    existing = db.query(Category).filter(Category.category_name == category_data.category_name).first()
    if existing:
        return existing

    category = Category(category_name=category_data.category_name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@category_router.get('/{category_id}/', response_model=CategoryOutputSchema, summary='Detail Category')
@category_router.get('/{category_id}', response_model=CategoryOutputSchema, include_in_schema=False)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория табылган жок")
    return category


@category_router.put('/{category_id}/', response_model=CategoryOutputSchema, summary='Update Category')
@category_router.put('/{category_id}', response_model=CategoryOutputSchema, include_in_schema=False)
async def update_category(
    category_id: int,
    category_data: CategoryCreateSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория табылган жок")

    category.category_name = category_data.category_name
    db.commit()
    db.refresh(category)
    return category


@category_router.delete('/{category_id}/', response_model=dict, summary='Delete Category')
@category_router.delete('/{category_id}', response_model=dict, include_in_schema=False)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория табылган жок")

    db.delete(category)
    db.commit()
    return {"message": "Категория ийгиликтүү өчүрүлдү"}
