from dataclasses import dataclass, field


@dataclass
class Command:
    name: str
    description: str
    args: list = field(default_factory=list)
    exec_func = None
