import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.business import Business
from app.models.integration import Integration, IntegrationStatus, IntegrationType
from app.models.user import User
from app.schemas.integration import IntegrationConnect, IntegrationResponse

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.post("/{business_id}/connect", response_model=IntegrationResponse)
async def connect_integration(
    business_id: str,
    data: IntegrationConnect,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Business).where(
            Business.id == uuid.UUID(business_id),
            Business.owner_id == current_user.id,
        )
    )
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    if data.type not in [t.value for t in IntegrationType]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid integration type")

    integration = Integration(
        business_id=business.id,
        type=data.type,
        status=IntegrationStatus.CONNECTED,
        credentials=data.credentials,
    )
    db.add(integration)
    await db.flush()
    await db.refresh(integration)
    return integration


@router.post("/{business_id}/csv-upload", response_model=IntegrationResponse)
async def upload_csv(
    business_id: str,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Business).where(
            Business.id == uuid.UUID(business_id),
            Business.owner_id == current_user.id,
        )
    )
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV")

    content = await file.read()

    from app.integrations.adapters.csv_adapter import CSVAdapter
    from app.repositories.transaction_repository import TransactionRepository

    adapter = CSVAdapter()
    adapter.load_csv(content)

    from datetime import date

    transactions = await adapter.sync_transactions(str(business.id), date.min, date.max)

    if transactions:
        txn_repo = TransactionRepository(db)
        await txn_repo.bulk_create(transactions)

    integration = Integration(
        business_id=business.id,
        type=IntegrationType.CSV,
        status=IntegrationStatus.CONNECTED,
        metadata_json={"filename": file.filename, "rows_imported": len(transactions)},
    )
    db.add(integration)
    await db.flush()
    await db.refresh(integration)
    return integration


@router.get("/{business_id}", response_model=list[IntegrationResponse])
async def list_integrations(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Integration).where(
            Integration.business_id == uuid.UUID(business_id),
        )
    )
    return list(result.scalars().all())
