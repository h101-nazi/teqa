from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.business import Business
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate

router = APIRouter(prefix="/businesses", tags=["Businesses"])


@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    data: BusinessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = BusinessRepository(db)
    business = Business(
        owner_id=current_user.id,
        name=data.name,
        industry=data.industry,
        country=data.country,
        currency=data.currency,
        whatsapp_number=data.whatsapp_number,
        timezone=data.timezone,
        is_onboarded=True,
    )
    business = await repo.create(business)
    return business


@router.get("/", response_model=list[BusinessResponse])
async def list_businesses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = BusinessRepository(db)
    return await repo.get_by_owner(current_user.id)


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import uuid

    repo = BusinessRepository(db)
    business = await repo.get_by_id(uuid.UUID(business_id))
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


@router.patch("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: str,
    data: BusinessUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import uuid

    repo = BusinessRepository(db)
    business = await repo.get_by_id(uuid.UUID(business_id))
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(business, key, value)

    return await repo.update(business)
