import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

# Get database URL from environment variable, fallback to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./user_service.db")

# Configure engine based on database type
if DATABASE_URL.startswith("postgresql"):
    # For PostgreSQL, add connection pooling settings to handle authentication issues
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,  # Number of connections to maintain
        max_overflow=10,  # Max connections beyond pool_size
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False  # Set to True for SQL debugging
    )
else:
    # SQLite configuration for fallback
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

#check if the database is connected write OK and if not write ERROR
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection():
    try:
        with engine.connect() as conn:
            print("Database connection successful")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
    
    
