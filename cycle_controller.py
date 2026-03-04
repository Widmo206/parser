"""CycleController class that routes events and uses a timer to send level cycle requests

Created on 2026.03.04
Contributors:
    Romcode
"""

import events


class CycleController:
    def __init__(self) -> None:
        events.StepForwardButtonPressed.connect(self._on_step_forward_button_pressed)

    def destroy(self) -> None:
        events.StepForwardButtonPressed.disconnect(self._on_step_forward_button_pressed)

    def run(self) -> None:
        ...

    def step_back(self) -> None:
        ...

    def step_forward(self) -> None:
        events.CycleRequested()

    def _on_step_forward_button_pressed(self, _event: events.StepForwardButtonPressed) -> None:
        self.step_forward()
