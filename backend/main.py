from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime
import uuid

from . import models, services, schemas
from .database import engine, SessionLocal, DATA_DIR

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ledger API")

# Setup CORS to allow the local frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # During development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/expenses/upload")
async def upload_receipt(file: UploadFile = File(...)):
    """
    Upload receipt image/PDF.
    Will call Claude API to extract merchant, date, amount, currency, and suggest a tax category.
    """
    if not file.content_type.startswith("image/") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Must be an image or PDF.")

    receipts_dir = os.path.join(DATA_DIR, "receipts")
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(receipts_dir, unique_filename)

    # Save the file locally
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Read the file contents back into memory for the API call
    # We run it synchronously here assuming small files, but real world might use async queueing
    with open(file_path, "rb") as f:
        file_content = f.read()

    # Call Anthropics API
    try:
        extracted_data = services.parse_receipt(file_content, file.content_type)
        extracted_data["receipt_url"] = f"/data/receipts/{unique_filename}"
        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude API extraction failed: {str(e)}")

@app.get("/api/expenses", response_model=List[schemas.ExpenseResponse])
def list_expenses(db: Session = Depends(get_db)):
    """
    Search & filter expenses (by category, date range, deductible status).
    For now, returns all descending by date.
    """
    return db.query(models.Expense).order_by(models.Expense.date.desc()).all()

@app.post("/api/expenses", response_model=schemas.ExpenseResponse)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    """
    Create a new expense manually or from a confirmed receipt upload.
    """
    db_expense = models.Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.put("/api/expenses/{expense_id}")
def update_expense(expense_id: int, db: Session = Depends(get_db)):
    return {"message": "Endpoint stubbed."}

@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    return {"message": "Endpoint stubbed."}

@app.get("/api/bills")
def list_bills(db: Session = Depends(get_db)):
    """
    List recurring bills.
    """
    return []

@app.post("/api/bills")
def create_bill(db: Session = Depends(get_db)):
    return {"message": "Endpoint stubbed."}

@app.put("/api/bills/{bill_id}")
def update_bill(bill_id: int, db: Session = Depends(get_db)):
    """
    Update a bill (e.g., mark as paid/unpaid).
    """
    return {"message": "Endpoint stubbed."}

@app.get("/api/dashboard/monthly")
def get_monthly_dashboard(db: Session = Depends(get_db)):
    """
    Monthly spend dashboard (spend by category, deductible YTD total).
    Primary currency: CAD, secondary: USD (converted).
    Includes total income from sources.
    """
    from sqlalchemy import func
    
    # Calculate expenses
    total_expenses = float(db.query(func.sum(models.Expense.amount)).scalar() or 0.0)
    deductible_expenses = float(db.query(func.sum(models.Expense.amount)).filter(models.Expense.is_deductible == True).scalar() or 0.0)
    
    # Calculate income
    total_income = float(db.query(func.sum(models.Income.amount)).scalar() or 0.0)
    
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "total_deductible": round(deductible_expenses, 2),
        "currency": "CAD"
    }

@app.get("/api/income")
def list_income(db: Session = Depends(get_db)):
    """
    List income sources (job, business projects, etc).
    """
    return []

@app.post("/api/income")
def create_income(db: Session = Depends(get_db)):
    return {"message": "Endpoint stubbed."}

@app.put("/api/income/{income_id}")
def update_income(income_id: int, db: Session = Depends(get_db)):
    return {"message": "Endpoint stubbed."}

@app.delete("/api/income/{income_id}")
def delete_income(income_id: int, db: Session = Depends(get_db)):
    return {"message": "Endpoint stubbed."}

@app.get("/api/export/csv")
def export_csv(db: Session = Depends(get_db)):
    """
    Export expenses data to CSV for tax time.
    """
    return {"message": "Endpoint stubbed."}
