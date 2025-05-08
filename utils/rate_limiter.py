import asyncio
import time

class RateLimiter:
    def __init__(self, max_rate):
        self.max_rate = max_rate
        self._lock = asyncio.Lock()
        self._tokens = max_rate
        self._last = time.monotonic()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            self._tokens += elapsed * self.max_rate
            if self._tokens > self.max_rate:
                self._tokens = self.max_rate
            self._last = now

            if self._tokens < 1:
                await asyncio.sleep((1 - self._tokens) / self.max_rate)
                self._tokens = 0
            else:
                self._tokens -= 1