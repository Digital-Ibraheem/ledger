from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Enum as SQLEnum, Text, ForeignKey
import enum
from database import Base

class CategoryEnum(str, enum.Enum):
    business = "business"
    donation = "donation"
    medical = "medical"
    personal = "personal"
    other = "other"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    merchant = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="CAD")  # "CAD" or "USD"
    category = Column(SQLEnum(CategoryEnum), nullable=False)
    is_deductible = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    receipt_url = Column(String, nullable=True)  # File path to stored image/PDF

class IncomeEnum(str, enum.Enum):
    job = "job"
    business = "business"
    other = "other"

class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="CAD")
    income_type = Column(SQLEnum(IncomeEnum), nullable=False)
    notes = Column(Text, nullable=True)

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="CAD")
    due_date = Column(Date, nullable=False)
    is_paid = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
