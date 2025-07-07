from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field, constr
from supabase import Client
from postgrest import APIResponse

from core.database.client import supabase

TABLE_NAME = "User Messages"


class Message(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    sender_id: str
    receiver_id: str
    content: constr(max_length=4096)

    class Config:
        from_attributes = True


def _as_model(resp: APIResponse) -> List[Message]:
    return [Message(**row) for row in resp.data]


def send(msg: Message, sb: Client = supabase) -> Message:
    resp = sb.table(TABLE_NAME).insert(msg.model_dump(exclude_none=True)).execute()
    return _as_model(resp)[0]


def inbox(user_id: str, sb: Client = supabase) -> List[Message]:
    resp = sb.table(TABLE_NAME).select("*").eq("receiver_id", user_id).execute()
    return _as_model(resp)
