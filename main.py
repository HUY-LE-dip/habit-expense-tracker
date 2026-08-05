import logging

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal, engine, Base
from models import Habit, HabitLog, Expense
from datetime import datetime, timedelta
from passlib.context import CryptContext
from models import User
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 


# Create all tables defined in models.py (if they don't already exist)
# This runs once when the app starts and builds tracker.db for real
Base.metadata.create_all(bind=engine)

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()
SECRET_KEY = "YOUR-SECRET-KEY-CHANGE-THIS-LATER"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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

# Returns total spending grouped by category
@app.get("/expenses/summary")
def get_expense_summary(db: Session = Depends(get_db)):
    results = (
        db.query(Expense.category, func.sum(Expense.amount).label("total"))
        .group_by(Expense.category)
        .all()
    )
    return [{"catergory": r.category, "total": r.total} for r in results]

#Calculates the current streak (consecutive days logged) for a habit
@app.get("/habits/{habit_id}/streak")
def get_habit_streak(habit_id: int, db: Session = Depends(get_db)):
    logs = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id)
        .order_by(HabitLog.log_date.desc())
        .all()
    )

    if not logs:
        return {"habit_id": habit_id, "streak": 0}

    # Get just the dates (ignoring time), removving duplicates same-day logs
    log_dates = sorted({log.log_date.date() for log in logs}, reverse=True)

    streak = 1
    today = log_dates[0]

    for i in range(1, len(log_dates)):
        expected_previous_day = today - timedelta(days=i)
        if log_dates[i] == expected_previous_day:
            streak += 1
        else:
            break   

    return {"habit_id": habit_id, "streak": streak}

@app.post("/signup")
def signup(username: str, password: str, db: Session = Depends (get_db)):
    #Check if the suername already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return {"error": "Username already exists"}

    # Hash the password before storing it
    hashed_password = pwd_context.hash(password)

    # Create a new user
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # Check if the user exists
    user = db.query(User).filter(User.username == username).first()

    if not user or not pwd_context.verify(password, user.hashed_password):
        return {"error": "Invalid username or password"}

    # Create a token tha expires in 60 minutes
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": user.username, "exp": expire}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@app.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}