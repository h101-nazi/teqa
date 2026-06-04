from pydantic import BaseModel


class BusinessCreate(BaseModel):
    name: str
    industry: str
    country: str = "Egypt"
    currency: str = "EGP"
    whatsapp_number: str
    timezone: str = "Africa/Cairo"


class BusinessUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    country: str | None = None
    currency: str | None = None
    whatsapp_number: str | None = None
    timezone: str | None = None


class BusinessResponse(BaseModel):
    id: str
    name: str
    industry: str
    country: str
    currency: str
    whatsapp_number: str
    timezone: str
    is_onboarded: bool

    model_config = {"from_attributes": True}
