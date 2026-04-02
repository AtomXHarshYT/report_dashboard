from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class LoginModel(BaseModel):
    employee_id: str
    password: str

class TicketCreate(BaseModel):
    user_id: str
    date: date
    ticket_id: Optional[str] = None
    rest_ids: List[str]
    vendor_ids: List[str]
    status: str
    remarks: List[str]

class TicketUpdate(BaseModel):
    date: date
    ticket_id: Optional[str] = None
    rest_ids: List[str]
    vendor_ids: List[str]
    status: str
    remarks: List[str]