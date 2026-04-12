from pydantic import BaseModel


class TaskSchema(BaseModel):
    title: str
    description: str
    completed: bool
    priority: int
