from typing import Optional
from libmuscle import Message


class ImplementationTester:
    def __init__(self, default_timeout: float) -> None: ...

    def send(
        self, port_name: str, message: Message, slot: Optional[int] = None
    ) -> None: ...

    def receive(
        self,
        port_name: str,
        slot: Optional[int] = None,
        *,
        timeout: Optional[float] = None,
    ) -> Message: ...
