from pydantic import BaseModel
from typing import List, Optional
import datetime

class LoginModel(BaseModel):
    employee_id: str
    password: str

class TicketCreate(BaseModel):
    user_id: str
    date: datetime.date
    ticket_id: Optional[str] = None
    rest_ids: List[str]
    vendor_ids: List[str]
    status: str
    remarks: List[str]

class TicketUpdate(BaseModel):
    date: Optional[datetime.date] = None
    ticket_id: Optional[str] = None
    rest_ids: Optional[List[str]] = None
    vendor_ids: Optional[List[str]] = None
    status: Optional[str] = None
    remarks: Optional[List[str]] = None