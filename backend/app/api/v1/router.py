from fastapi import APIRouter

from app.api.v1.endpoints import auth, billing, business, integrations, reports

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(business.router)
api_router.include_router(integrations.router)
api_router.include_router(reports.router)
api_router.include_router(billing.router)
