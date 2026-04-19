from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings
import os

# 🔥 najpierw próbujemy Railway, potem lokalnie
DATABASE_URL = os.getenv("DATABASE_URL") or settings.database_url

# 🔥 FIX dla Railway (postgres:// → postgresql+psycopg2://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg2://",
        1  # tylko pierwsze wystąpienie (bezpieczniej)
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()