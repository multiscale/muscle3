from dataclasses import dataclass
from pathlib import Path


class AgentCommand:
    pass


@dataclass
class StartCommand(AgentCommand):
    name: str
    work_dir: Path
    args: list[str]
    env: dict[str, str]
    stdout: Path
    stderr: Path


class CancelAllCommand(AgentCommand):
    pass


class ShutdownCommand(AgentCommand):
    pass
