from pydantic import BaseModel
from typing import Optional


class GameCreate(BaseModel):
    name: str
    rawg_id: int
    background_img: Optional[str] = None
    platforms: Optional[str] = None
    comment: Optional[str] = None
    rating: Optional[int] = None
    progress: Optional[str] = None

class GameUpdate(BaseModel):
    comment: Optional[str] = None
    rating: Optional[int] = None
    progress: Optional[str] = None