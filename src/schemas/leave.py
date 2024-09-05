from pydantic import BaseModel, Field
from typing import Optional
from datetime import date,datetime
from enum import Enum

class LeaveDuration(str, Enum):
    ONE_DAY = "one_day"
    HALF_DAY = "half_day"

class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class EmployeeLeaveBase(BaseModel):
    leave_type: str
    duration: LeaveDuration
    start_date: date
    total_days: int = Field(gt=0)
    reason: Optional[str] = None

class EmployeeLeaveCreate(EmployeeLeaveBase):
    pass

class EmployeeLeaveUpdate(BaseModel):
    leave_id:int
    employee_id:str
    status: Optional[LeaveStatus] = None
    reason: Optional[str] = None

class EmployeeLeaveResponse(BaseModel):
    id: int
    employee_id: int
    report_manager_id: int
    leave_type: str
    duration: LeaveDuration
    start_date: date
    end_date: date
    status: LeaveStatus
    reason: Optional[str] = None
    reject_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
