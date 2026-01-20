from datetime import date
from pydantic import BaseModel, Field
from typing import Literal

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    password: str
    role: Literal["employee", "manager", "hr"]


class Login(BaseModel):
    username: str
    password: str

class LeaveCreate(BaseModel):
    from_date: date
    to_date: date
    reason: str
class RejectLeave(BaseModel):
    reason: str
