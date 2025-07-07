from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field, constr
from supabase import Client
from postgrest import APIResponse

from core.database.client import supabase

TABLE_NAME = "User Ledger"


class UserLedger(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    username: constr(strip_whitespace=True, min_length=3)
    user_id: Optional[str] = None
    password: str

    class Config:
        from_attributes = True


def _as_model(resp: APIResponse) -> List[UserLedger]:
    """Convert supabase response to list of models."""
    return [UserLedger(**row) for row in resp.data]


def create(user: UserLedger, sb: Client = supabase) -> UserLedger:
    resp = sb.table(TABLE_NAME).insert(user.model_dump(exclude_none=True)).execute()
    return _as_model(resp)[0]


def get_by_username(username: str, sb: Client = supabase) -> Optional[UserLedger]:
    resp = sb.table(TABLE_NAME).select("*").eq("username", username).limit(1).execute()
    return _as_model(resp)[0] if resp.data else None


def update_password(
    username: str, new_pwd_hash: str, sb: Client = supabase
) -> UserLedger:
    resp = (
        sb.table(TABLE_NAME)
        .update({"password": new_pwd_hash})
        .eq("username", username)
        .execute()
    )
    return _as_model(resp)[0]


def delete(username: str, sb: Client = supabase) -> None:
    sb.table(TABLE_NAME).delete().eq("username", username).execute()
