from typing import Optional
from dataclasses import dataclass

@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    deadline: str = ""
    status: str = "pending"
    category: str = "ToDo"
