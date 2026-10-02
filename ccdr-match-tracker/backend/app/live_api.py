from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.live_schemas import EventCreate, EventRead, EventUpdate, LiveState, Transition
from app import live_service as live
from app.match_service import get_match
from app.models import Match

router = APIRouter(prefix="/matches/{match_id}", tags=["live"])
Database = Annotated[Session, Depends(get_db)]


def mutate(db: Session, match_id: int, operation: Callable[[Match], object]) -> LiveState:
    try:
        match = get_match(db, match_id, lock=True)
        operation(match)
        db.flush()
        response = live.state(db, match)
        db.commit()
        return response
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Dados do jogo em conflito. Recarregue e tente novamente.") from None
    except Exception:
        db.rollback()
        raise


@router.get("/live", response_model=LiveState)
def live_state(match_id: int, db: Database):
    # Same row lock as writers: score, timeline and clock form one coherent snapshot.
    return live.state(db, get_match(db, match_id, lock=True))


@router.post("/transition", response_model=LiveState)
def change_state(match_id: int, payload: Transition, db: Database):
    return mutate(db, match_id, lambda match: live.transition(match, payload.status, live.utcnow()))


@router.get("/events", response_model=list[EventRead])
def list_events(match_id: int, db: Database):
    get_match(db, match_id)
    return live.events(db, match_id)


@router.post("/events", response_model=LiveState, status_code=201)
def create_event(match_id: int, payload: EventCreate, db: Database):
    return mutate(db, match_id, lambda match: live.create_event(db, match, payload))


@router.patch("/events/{event_id}", response_model=LiveState)
def edit_event(match_id: int, event_id: int, payload: EventUpdate, db: Database):
    return mutate(db, match_id, lambda match: live.update_event(db, match, event_id, payload))


@router.delete("/events/{event_id}", response_model=LiveState)
def delete_event(match_id: int, event_id: int, db: Database):
    return mutate(db, match_id, lambda match: db.delete(live.get_event(db, match.id, event_id)))
