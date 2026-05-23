from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from typing import Generator


DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ghost_inventory_db"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_session() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
