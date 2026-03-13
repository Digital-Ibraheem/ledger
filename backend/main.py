from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List

from . import models
from .database import engine, SessionLocal

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ledger API")

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
    return {"message": "Endpoint stubbed. Will process receipt and return structured JSON."}

@app.get("/api/expenses")
def list_expenses(db: Session = Depends(get_db)):
    """
    Search & filter expenses (by category, date range, deductible status).
    """
    return []

@app.post("/api/expenses")
def create_expense(db: Session = Depends(get_db)):
    """
    Create a new expense manually or from a confirmed receipt upload.
    """
    return {"message": "Endpoint stubbed."}

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
    return {"message": "Endpoint stubbed."}

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
