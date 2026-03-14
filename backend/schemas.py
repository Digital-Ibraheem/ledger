from pydantic import BaseModel
from datetime import date
from typing import Optional

# Base for Enums from models
from .models import CategoryEnum, IncomeEnum

# --- Expenses ---
class ExpenseCreate(BaseModel):
    merchant: str
    date: date
    amount: float
    currency: str = "CAD"
    category: CategoryEnum
    is_deductible: bool = False
    notes: Optional[str] = None
    receipt_url: Optional[str] = None

class ExpenseResponse(ExpenseCreate):
    id: int

    class Config:
        from_attributes = True

# --- Income ---
class IncomeCreate(BaseModel):
    source: str
    date: date
    amount: float
    currency: str = "CAD"
    income_type: IncomeEnum
    notes: Optional[str] = None

class IncomeResponse(IncomeCreate):
    id: int

    class Config:
        from_attributes = True

# --- Bills ---
class BillCreate(BaseModel):
    title: str
    amount: float
    currency: str = "CAD"
    due_date: date
    is_paid: bool = False
    is_recurring: bool = False

class BillResponse(BillCreate):
    id: int

    class Config:
        from_attributes = True
