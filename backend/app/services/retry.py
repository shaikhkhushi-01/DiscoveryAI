import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar
T=TypeVar("T")
async def with_retry(fn: Callable[[], Awaitable[T]], attempts: int = 3, base_delay: float = 0.5) -> T:
    last: Exception | None = None
    for attempt in range(attempts):
        try: return await fn()
        except Exception as exc:
            last=exc
            if attempt + 1 < attempts: await asyncio.sleep(base_delay * (2 ** attempt))
    assert last is not None
    raise last
