"""İş başına SSE olay yolu."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[asyncio.Queue]] = {}

    def subscribe(self, job_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._subs.setdefault(job_id, []).append(q)
        return q

    def unsubscribe(self, job_id: str, q: asyncio.Queue) -> None:
        subs = self._subs.get(job_id, [])
        if q in subs:
            subs.remove(q)
        if not subs:
            self._subs.pop(job_id, None)

    async def publish(self, job_id: str, event_type: str, **data) -> None:
        event = {"type": event_type, "job_id": job_id,
                 "ts": datetime.now(timezone.utc).isoformat(), **data}
        for q in list(self._subs.get(job_id, [])):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass


bus = EventBus()
