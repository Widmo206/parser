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
        events.RestartButtonPressed.connect(self._on_restart_button_pressed)
        events.StepBackButtonPressed.connect(self._on_step_back_button_pressed)
        events.StepForwardButtonPressed.connect(self._on_step_forward_button_pressed)

    def destroy(self) -> None:
        events.RestartButtonPressed.disconnect(self._on_restart_button_pressed)
        events.StepBackButtonPressed.disconnect(self._on_step_back_button_pressed)
        events.StepForwardButtonPressed.disconnect(self._on_step_forward_button_pressed)

    def start(self) -> None:
        self.is_running = True
        events.CyclingStarted()
        self._cycle()

    def step_back(self) -> None:
        # TODO: ughhhh time travel
        ...

    def step_forward(self) -> None:
        events.CycleRequested()

    def stop(self) -> None:
        self.scheduler.after_cancel(self.after_id)
        self.is_running = False
        self.after_id = None
        events.CyclingStopped()

    def _cycle(self) -> None:
        if not self.is_running:
            return

        self.step_forward()
        self.after_id = self.scheduler.after(250, self._cycle)

    def _on_restart_button_pressed(self, _event: events.RestartButtonPressed) -> None:
        if self.is_running:
            self.stop()

    def _on_step_back_button_pressed(self, _event: events.StepBackButtonPressed) -> None:
        if self.is_running:
            self.stop()
        self.step_back()

    def _on_step_forward_button_pressed(self, _event: events.StepForwardButtonPressed) -> None:
        if self.is_running:
            self.stop()
        self.step_forward()
