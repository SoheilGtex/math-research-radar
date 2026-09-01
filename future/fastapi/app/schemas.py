from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PaperResponse(BaseModel):
    id: str
    title: str
    published: str
    summary: Optional[str] = None
    link: str
    category: str
    source: str
    created_at: Optional[datetime] = None

    # Allows Pydantic to read data directly from SQLAlchemy ORM objects
    model_config = ConfigDict(from_attributes=True)