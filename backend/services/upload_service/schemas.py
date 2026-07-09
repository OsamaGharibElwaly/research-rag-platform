"""Upload service Pydantic schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    created_at: datetime
