"""Module to create dataclass ExecutionContext"""

from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import os

@dataclass
class ExecutionContext():
    """A data class that stores context of when and where a command was run."""
    cwd: Path
    time: datetime
    machine: str
    user: str

    def __init__(self):
        """Initialize the ExecutionContext with the current working directory and time."""
        self.cwd = Path.cwd()
        self.time = datetime.now()
        self.machine = os.environ.get("HOST", "")
        self.user = os.environ.get("USER", "")

    def to_dict(self):
        """Return a dictionary with this class' data"""

        return {
            "cwd": str(self.cwd),
            "time": self.time.isoformat(),
            "machine": self.machine,
            "user": self.user
        }

    @classmethod
    def from_dict(cls,data : dict):
        """Return an ExecutionContext object from a dict"""

        obj = cls.__new__(cls)
        obj.cwd = Path(data["cwd"])
        obj.time = datetime.fromisoformat(data["time"])
        obj.machine = data["machine"]
        obj.user = data["user"]
        return obj
