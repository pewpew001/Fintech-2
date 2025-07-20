from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class POSTerminalBase(BaseModel):
    terminal_name: str
    terminal_id: str
    trsm: Optional[str] = None
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    branch: Optional[str] = None
    merchant_name: str
    bank: Optional[str] = None
    device_type: Optional[str] = None
    mcc_code: Optional[str] = None


class POSTerminalCreate(POSTerminalBase):
    pass


class POSTerminalUpdate(BaseModel):
    terminal_name: Optional[str] = None
    trsm: Optional[str] = None
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    branch: Optional[str] = None
    merchant_name: Optional[str] = None
    bank: Optional[str] = None
    device_type: Optional[str] = None
    mcc_code: Optional[str] = None


class POSTerminalResponse(POSTerminalBase):
    id: int
    last_transaction_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True