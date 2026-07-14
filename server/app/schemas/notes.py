from pydantic import BaseModel
from datetime import datetime

class CreateNote(BaseModel):
    title: str
    content: str

class NoteResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    content: str
    create_at: datetime
    update_at: datetime