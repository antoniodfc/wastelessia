import json
import os
import queue
import threading

import httpx

from ._config import get_config

_DEBUG = os.environ.get("WASTELESSIA_DEBUG", "").lower() in ("1", "true", "yes")

_queue: queue.Queue = queue.Queue()
_worker: threading.Thread | None = None
_lock = threading.Lock()


def _start_worker() -> None:
    global _worker
    with _lock:
        if _worker is None or not _worker.is_alive():
            _worker = threading.Thread(target=_consume, daemon=True)
            _worker.start()


def _consume() -> None:
    while True:
        event = _queue.get()
        if event is None:
            break
        config = get_config()
        if _DEBUG:
            print(f"[wastelessia] {json.dumps(event)}", flush=True)
        if config.api_key:
            try:
                httpx.post(
                    f"{config.endpoint}/v1/events",
                    json=event,
                    headers={"Authorization": f"Bearer {config.api_key}"},
                    timeout=5,
                )
            except Exception:
                pass  # fire-and-forget: never block the caller
        _queue.task_done()


def send_event_async(event: dict) -> None:
    _start_worker()
    _queue.put(event)
