from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.auth_service import AuthService

from .provider_controller import ProviderController
from .provider_schema import GetProviderResponse, ProviderInfo, SetProviderRequest
import os
litellm_provider = os.getenv("LITELLM_PROVIDER")
router = APIRouter()


class ProviderAPI:
    @staticmethod
    @router.get("/list-available-llms/", response_model=List[ProviderInfo])
    async def list_available_llms(
        db: Session = Depends(get_db),
        user=Depends(AuthService.check_auth),
    ):
        user_id = user["user_id"]
        controller = ProviderController(db, user_id)
        return await controller.list_available_llms()

    @staticmethod
    @router.post("/set-global-ai-provider/")
    async def set_global_ai_provider(
        provider_request: SetProviderRequest,
        db: Session = Depends(get_db),
        user=Depends(AuthService.check_auth),
    ):
        user_id = user["user_id"]
        controller = ProviderController(db, user_id)
        return await controller.set_global_ai_provider(
            user["user_id"], litellm_provider
        )

    @staticmethod
    @router.get("/get-global-ai-provider/")
    async def get_global_ai_provider(
        db: Session = Depends(get_db),
        user=Depends(AuthService.check_auth),
    ):
        user_id = user["user_id"]
        controller = ProviderController(db, user_id)
        return await controller.get_global_ai_provider(user_id)

    @staticmethod
    @router.get("/get-preferred-llm/", response_model=GetProviderResponse)
    async def get_preferred_llm(
        user_id: str,
        db: Session = Depends(get_db),
        hmac_signature: str = Header(..., alias="X-HMAC-Signature"),
    ):
        if not AuthService.verify_hmac_signature(user_id, hmac_signature):
            raise HTTPException(status_code=401, detail="Unauthorized")
        controller = ProviderController(db, user_id)
        return await controller.get_preferred_llm(user_id)
