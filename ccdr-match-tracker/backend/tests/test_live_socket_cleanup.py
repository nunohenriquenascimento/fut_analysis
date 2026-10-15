"""Exercise cancellation without PostgreSQL or the TestClient transport."""
import asyncio

import anyio

from app import live_socket


def test_socket_cancellation_releases_subscription_and_child_tasks(monkeypatch):
    async def exercise():
        sent = anyio.Event()

        class Socket:
            headers = {"origin": live_socket.get_settings().cors_origins[0]}
            cookies = {}

            async def accept(self):
                pass

            async def send_json(self, message):
                sent.set()

            async def receive_text(self):
                await anyio.sleep_forever()

            async def close(self, **kwargs):
                pass

        baseline = set(asyncio.all_tasks())
        hub = live_socket.MatchLiveHub()
        monkeypatch.setattr(live_socket, "hub", hub)
        monkeypatch.setattr(live_socket, "read_connection", lambda *args: {})
        async with anyio.create_task_group() as group:
            group.start_soon(live_socket.match_live_socket, Socket(), 123)
            await sent.wait()
            # Let the handler start its send/receive tasks, then cancel its scope.
            for _ in range(5):
                await anyio.sleep(0)
            group.cancel_scope.cancel()
        assert hub.rooms == {}, "Cancelled socket retained its subscription"
        await anyio.sleep(0)
        pending = set(asyncio.all_tasks()) - baseline
        assert not pending, "Cancelled socket left background tasks running"

    anyio.run(exercise)
