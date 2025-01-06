from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


class AgentCommand:
    pass


@dataclass
class StartCommand(AgentCommand):
    name: str
    work_dir: Path
    args: List[str]
    env: Dict[str, str]
    stdout: Path
    stderr: Path


class CancelAllCommand(AgentCommand):
    pass


class ShutdownCommand(AgentCommand):
    pass
