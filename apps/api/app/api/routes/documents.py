from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.schemas.documents import DocumentRead
from app.services.demo_data import DEMO_DOCUMENTS

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRead])
def list_documents(user: CurrentUser = Depends(get_current_user)) -> list[DocumentRead]:
    return [document for document in DEMO_DOCUMENTS if document.plant_id == user.plant_id]
