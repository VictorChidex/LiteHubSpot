import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Prefer explicit DATABASE_URL env var (for Postgres). Otherwise use
# a sqlite file stored at backend/db.sqlite3 so it's easy to find.
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URL')

# Ensure we default to a stable, absolute sqlite path inside the backend
if not DATABASE_URL:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.makedirs(BASE_DIR, exist_ok=True)
    DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')
    # Touch the file to make its existence explicit (create on disk)
    if not os.path.exists(DB_PATH):
        open(DB_PATH, 'a').close()
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# Use check_same_thread=False for sqlite when Django/dev server reloaders
# may access the DB from multiple threads
connect_args = {}
if DATABASE_URL.startswith('sqlite:///'):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def init_db():
    # Import models here to ensure they are registered on Base, then create tables
    from . import sql_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
