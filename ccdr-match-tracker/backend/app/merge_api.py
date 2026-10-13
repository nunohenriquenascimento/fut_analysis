import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import Admin
from app.database import get_db
from app import live_service, merge_service as merge
from app.live_schemas import LiveState
from app.live_socket import notify_live
from app.merge_schemas import MergeExecute, MergePreview, MergeSelection

router = APIRouter(prefix="/matches/merge", tags=["merge"])
Database = Annotated[Session, Depends(get_db)]
logger = logging.getLogger(__name__)


@router.post("/preview", response_model=MergePreview)
def preview_merge(payload: MergeSelection, db: Database, admin: Admin):
    principal, continuation = merge.lock_games(db, payload)
    preview = merge.plan(db, principal, continuation, payload)
    if preview.can_merge:
        preview.preview_token = merge.token(merge.fingerprint(db, principal, continuation, preview), admin.id)
    return preview


@router.post("", response_model=LiveState)
def execute_merge(payload: MergeExecute, db: Database, admin: Admin):
    try:
        principal, continuation = merge.lock_games(db, payload)
        preview = merge.plan(db, principal, continuation, payload)
        if not preview.can_merge:
            raise HTTPException(409, " ".join(preview.conflicts))
        merge.verify_token(payload.preview_token, merge.fingerprint(db, principal, continuation, preview), admin.id)
        merge.apply(db, principal, continuation, preview)
        response = live_service.state(db, principal)
        db.commit()
        notify_live(payload.principal_id, "live.state_changed", admin.id)
        notify_live(payload.continuation_id, "live.match_updated", admin.id)
        logger.info("Matches merged principal_id=%s continuation_id=%s actor_id=%s", payload.principal_id, payload.continuation_id, admin.id)
        return response
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Existe uma dependência/conflito impeditivo. Nenhum jogo foi unido.") from None
    except Exception:
        db.rollback()
        raise
