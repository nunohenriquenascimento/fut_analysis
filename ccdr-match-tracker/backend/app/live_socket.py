"""Single-process Live notifications, separate from authoritative HTTP rules."""
import asyncio
from dataclasses import dataclass, field
import logging
from typing import Literal

from anyio import from_thread, to_thread
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import cookie_name, session_user
from app.config import get_settings
from app.database import get_engine
from app.live_service import state
from app.match_service import get_match

router = APIRouter(tags=["live websocket"])
logger = logging.getLogger(__name__)
CHECK_INTERVAL = 15
MessageType = Literal["live.snapshot", "live.state_changed", "live.event_created", "live.event_updated",
                      "live.event_deleted", "live.match_updated", "live.cancelled", "live.ping"]


class LiveMessage(BaseModel):
    type: MessageType
    match_id: int
    version: Literal[1] = 1
    actor_id: int | None = None
    data: dict = Field(default_factory=dict)


@dataclass(eq=False)
class Subscription:
    # Bounded queues prevent a suspended browser from consuming unbounded memory.
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=32))


class MatchLiveHub:
    def __init__(self):
        self.rooms: dict[int, set[Subscription]] = {}

    def subscribe(self, match_id: int) -> Subscription:
        subscriber = Subscription()
        self.rooms.setdefault(match_id, set()).add(subscriber)
        return subscriber

    def unsubscribe(self, match_id: int, subscriber: Subscription):
        room = self.rooms.get(match_id)
        if room is not None:
            room.discard(subscriber)
            if not room:
                self.rooms.pop(match_id, None)

    async def publish(self, match_id: int, kind: MessageType, actor_id: int | None):
        message = LiveMessage(type=kind, match_id=match_id, actor_id=actor_id).model_dump(mode="json")
        for subscriber in tuple(self.rooms.get(match_id, ())):
            if subscriber.queue.full():
                # Notifications are invalidations, not deltas: one latest refresh suffices.
                subscriber.queue.get_nowait()
            subscriber.queue.put_nowait(message)


hub = MatchLiveHub()


def notify_live(match_id: int, kind: MessageType, actor_id: int | None = None):
    """Called only AFTER commit from FastAPI's AnyIO worker thread."""
    try:
        from_thread.run(hub.publish, match_id, kind, actor_id)
    except Exception:
        # Never turn a committed write into an apparent HTTP failure/retry.
        logger.exception("Live notification unavailable for match %s", match_id)


def read_connection(token: str | None, match_id: int, snapshot: bool = False):
    # A fresh, short transaction each time: no DB connection kept for the socket lifetime.
    with Session(get_engine()) as db:
        session_user(db, token)
        match = get_match(db, match_id, lock=snapshot)
        return state(db, match).model_dump(mode="json") if snapshot else None


def close_code(error: HTTPException) -> int:
    return 4401 if error.status_code == 401 else 4404 if error.status_code == 404 else 4409


@router.websocket("/ws/matches/{match_id}/live")
async def match_live_socket(websocket: WebSocket, match_id: int):
    if websocket.headers.get("origin") not in get_settings().cors_origins:
        await websocket.close(code=4403)
        return
    token = websocket.cookies.get(cookie_name())
    try:
        await to_thread.run_sync(read_connection, token, match_id)
    except HTTPException as exc:
        await websocket.close(code=close_code(exc))
        return
    except Exception:
        await websocket.close(code=1013)
        return
    await websocket.accept()
    subscriber = hub.subscribe(match_id)

    async def receive():
        while True:
            # This channel never performs writes or accepts client identity.
            if await websocket.receive_text() != "pong":
                await websocket.close(code=1008)
                return

    async def send():
        while True:
            try:
                message = await asyncio.wait_for(subscriber.queue.get(), timeout=CHECK_INTERVAL)
            except asyncio.TimeoutError:
                message = LiveMessage(type="live.ping", match_id=match_id).model_dump(mode="json")
            # Also validate before each notification: revoked accounts receive no new state.
            await to_thread.run_sync(read_connection, token, match_id)
            await asyncio.wait_for(websocket.send_json(message), timeout=5)

    tasks = []
    try:
        initial = await to_thread.run_sync(read_connection, token, match_id, True)
        await asyncio.wait_for(websocket.send_json(LiveMessage(type="live.snapshot", match_id=match_id, data=initial).model_dump(mode="json")), timeout=5)
        tasks = [asyncio.create_task(receive()), asyncio.create_task(send())]
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            task.result()
    except HTTPException as exc:
        await websocket.close(code=close_code(exc))
    except (WebSocketDisconnect, RuntimeError):
        pass
    except Exception:
        try:
            await websocket.close(code=1013)
        except RuntimeError:
            pass
    finally:
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        hub.unsubscribe(match_id, subscriber)
