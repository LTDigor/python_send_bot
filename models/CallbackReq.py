from typing import Optional, Any

from pydantic import BaseModel


class CallbackReq(BaseModel):
    type: str
    group_id: int
    event_id: Optional[str] = None
    v: Optional[str] = None
    object: Optional[dict] = None
