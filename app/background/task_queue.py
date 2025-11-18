import threading
import queue
import time
from typing import Callable, Dict, Any


class TaskQueue:
    def __init__(self):
        self.queue = queue.Queue()
        self.handlers: Dict[str, Callable] = {}
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()

    def register(self, task_name: str, handler: Callable):
        self.handlers[task_name] = handler

    def enqueue(self, task_name: str, payload: Dict[str, Any]):
        self.queue.put((task_name, payload))

    def _worker_loop(self):
        while True:
            task_name, payload = self.queue.get()
            handler = self.handlers.get(task_name)
            if handler:
                try:
                    handler(payload)
                except Exception:
                    print(f"[TASK ERROR] {task_name}", flush=True)
            self.queue.task_done()


task_queue = TaskQueue()
