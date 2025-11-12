from typing import Dict
from threading import Lock

# Very small in-process counters (per worker)
class Metrics:
    _counters: Dict[str, int] = {}
    _lock = Lock()

    @classmethod
    def inc(cls, key: str, amt: int = 1):
        with cls._lock:
            cls._counters[key] = cls._counters.get(key, 0) + amt

    @classmethod
    def dump_prometheus(cls) -> str:
        # simple format: each counter as key value
        with cls._lock:
            lines = []
            for k, v in sorted(cls._counters.items()):
                safe = k.replace(" ", "_").replace("-", "_")
                lines.append(f"{safe} {v}")
            return "\n".join(lines) + "\n"

metrics = Metrics
