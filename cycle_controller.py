"""CycleController class that routes events and uses a timer to send level cycle requests

Created on 2026.03.04
Contributors:
    Romcode
"""

import events
from scheduler import Scheduler


class CycleController:
    scheduler: Scheduler
    is_running: bool
    after_id: str | None

    def __init__(self, scheduler: Scheduler) -> None:
        self.scheduler = scheduler
        self.is_running = False
        self.after_id = None

    def start(self) -> None:
        self.is_running = True
        events.CyclingStarted()
        self._cycle()

    def stop(self) -> None:
        if not self.is_running:
            return

        self.scheduler.after_cancel(self.after_id)
        self.is_running = False
        self.after_id = None
        events.CyclingStopped()

    def _cycle(self) -> None:
        if not self.is_running:
            return

        events.Cycled()
        self.after_id = self.scheduler.after(250, self._cycle)
