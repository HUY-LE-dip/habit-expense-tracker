from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

# This class represents a table in the database called "habits".
# Each instance of this class = one row in that table.
class Habit(Base):
    __tablename__ = "habits"

    # A unique ID for each habit, automatically assigned and indexed
    # (indexing makes lookups by id fast)
    id = Column(Integer, primary_key=True, index=True)

    # The name of the habit, e.g. "Read 20 minutes"
    # index=True makes searching/filtering by name faster    
    name = Column(String, index=True)

    # The date and time this habit was first created
    # defaults automatically to "now" if not provided
    created_at = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import ForeignKey

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    #Links this log entry back to a specific habit
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    #The date this habit was marked done
    log_date = Column(DateTime, default=datetime.utcnow)

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    # The amount spent, e.g. 12.50
    amount = Column(Integer)
    # A category label, e.g. "food", "transport"
    category = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow)

