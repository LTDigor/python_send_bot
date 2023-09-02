from typing import List, Optional
from pydantic import BaseModel


class SendMessagesReq(BaseModel):
    mailing_type: int
    message: str
    user_ids: Optional[List[int]] = None
