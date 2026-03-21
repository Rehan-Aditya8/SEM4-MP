from typing import Optional
from dataclasses import dataclass

@dataclass
class Event:
    id: Optional[int] = None
    title: str = ""
    start_time: str = ""
    end_time: str = ""
    location: str = ""
