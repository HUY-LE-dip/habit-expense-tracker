import logging

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Habit, HabitLog, Expense

# Create all tables defined in models.py (if they don't already exist)
# This runs once when the app starts and builds tracker.db for real
Base.metadata.create_all(bind=engine)

app = FastAPI()

# This function opens a database session for a request, and makes sure
# it's closed afterawards - FastAPI wil call this automatically wherever
# it's needed via Depends()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "ok"}

# Creates a new habit and saves it to the database
@app.post("/habits")
def create_habit(name: str, db: Session = Depends(get_db)):
    new_habit = Habit(name=name)
    db.add(new_habit)      # stage the new row
    db.commit()            # save it to the database
    db.refresh(new_habit)  # reload it so we get the auto-generated ID
    return new_habit

# Fetches all habits currently in the database
@app.get("/habits")
def get_habits(db: Session = Depends(get_db)):
    results = db.query(Habit).all()
    logging.warning(f"DEBUG: found {len(results)} habits)")
    return results

# Marks a habit as done for today
@app.post("/habits/{habit_id}/log")
def log_habit(habit_id: int, db: Session = Depends(get_db)):
    # Check if the habit exists
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        return {"error": "Habit not found"}

    # Create a new log entry for this habit
    new_log = HabitLog(habit_id=habit_id)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

# Creates a mew expense entry
@app.post("/expenses")
def create_expense(amount: int, category: str, db: Session = Depends(get_db)):
    new_expense = Expense(amount=amount, category=category)
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

# Fetches all expenses
@app.get("/expenses")
def get_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).all()
