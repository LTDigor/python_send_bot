from typing import Optional

from pydantic import BaseModel, Json


class Payload(BaseModel):
    command: Optional[str] = None
    type: Optional[str] = None
    mailing_id: Optional[int] = None


class Message(BaseModel):
    date: int
    from_id: int
    id: int
    out: int
    attachments: list
    conversation_message_id: int
    fwd_messages: list
    important: bool
    is_hidden: bool
    peer_id: int
    random_id: int
    text: str
    payload: Optional[Json[Payload]] = None


class ClientInfo(BaseModel):
    button_actions: list
    keyboard: bool
    inline_keyboard: bool
    carousel: bool
    lang_id: int


class CallbackObject(BaseModel):
    message: Message
    client_info: ClientInfo


class CallbackReq(BaseModel):
    type: str
    group_id: int
    event_id: Optional[str] = None
    v: Optional[str] = None
    object: Optional[CallbackObject] = None
