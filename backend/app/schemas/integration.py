from pydantic import BaseModel


class IntegrationConnect(BaseModel):
    type: str
    credentials: dict | None = None


class IntegrationResponse(BaseModel):
    id: str
    type: str
    status: str
    last_sync_at: str | None = None

    model_config = {"from_attributes": True}
