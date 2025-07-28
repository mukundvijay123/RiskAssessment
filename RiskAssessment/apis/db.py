# db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .tables import Base

# Supabase credentials
DB_USER = "postgres.oucktnjljscewmgoukzd"
DB_PASSWORD = "Ey-cat$2025"
DB_HOST = "aws-0-ap-south-1.pooler.supabase.com"
DB_PORT = 6543
DB_NAME = "postgres"

# Full SQLAlchemy connection URL (with SSL)
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?sslmode=require"
)

# Create engine with connection pool
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base.metadata.create_all(bind=engine)
# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Dependency to use in FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

