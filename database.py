from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The location of our database file — SQLite stores everything in a single
# local file called tracker.db, which will be created automatically
DATABASE_URL = "sqlite:///./tracker.db"

# The "engine" is the actual connection to the database file
# check_same_thread=False is needed because FastAPI can handle multiple
# requests at once, and SQLite needs to allow that
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is a factory for creating a new "session" — think of a
# session as a temporary conversation with the database that you open,
# use to read/write data, then close
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is a starting point that all our table models will inherit from,
# so SQLAlchemy knows to treat them as database tables
Base = declarative_base()

