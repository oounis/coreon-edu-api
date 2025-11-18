from __future__ import annotations
from typing import Dict, Any, Optional
from collections import defaultdict
import threading
import time


class Metrics:
    """
    Very simple in-memory metrics collector.

    - Counters: increment-only values
    - Timers: list of observed durations (ms)
    """

    def __init__(self):
        self._counters = defaultdict(int)
        self._timers = defaultdict(list)
        self._lock = threading.Lock()

    def _build_key(self, name: str, labels: Optional[Dict[str, Any]]) -> str:
        if not labels:
            return name
        # stable ordering
        parts = [f"{k}={labels[k]}" for k in sorted(labels.keys())]
        return f"{name}|{'|'.join(parts)}"

    def inc(self, name: str, value: int = 1, labels: Optional[Dict[str, Any]] = None) -> None:
        key = self._build_key(name, labels)
        with self._lock:
            self._counters[key] += value

    def observe(self, name: str, value_ms: float, labels: Optional[Dict[str, Any]] = None) -> None:
        key = self._build_key(name, labels)
        with self._lock:
            self._timers[key].append(float(value_ms))

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            counters = dict(self._counters)
            timers_summary: Dict[str, Any] = {}
            for key, values in self._timers.items():
                if not values:
                    continue
                vmin = min(values)
                vmax = max(values)
                avg = sum(values) / len(values)
                timers_summary[key] = {
                    "count": len(values),
                    "min_ms": vmin,
                    "max_ms": vmax,
                    "avg_ms": avg,
                }
        return {
            "counters": counters,
            "timers": timers_summary,
            "generated_at": time.time(),
        }


metrics = Metrics()
