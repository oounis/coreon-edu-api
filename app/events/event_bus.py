from typing import Callable, Dict, List
from app.events.domain_event import DomainEvent
from app.monitoring.metrics import metrics


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, handler: Callable):
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def publish(self, event: DomainEvent):
        handlers = self._handlers.get(event.event, [])
        payload = event.to_dict()

        # Metrics: event published
        try:
            metrics.inc(
                "domain_events_published_total",
                labels={"event": event.event},
            )
        except Exception:
            pass

        for h in handlers:
            # Metrics: handler invocation
            try:
                metrics.inc(
                    "domain_event_handler_invocations_total",
                    labels={"event": event.event, "handler": h.__name__},
                )
            except Exception:
                pass
            h(payload)


event_bus = EventBus()
