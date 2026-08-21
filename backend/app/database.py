from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from .models import Base

engine = create_engine("sqlite:///./aegisgrid.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    columns = {column["name"] for column in inspect(engine).get_columns("users")}
    additions = {
        "first_name": "TEXT DEFAULT ''",
        "last_name": "TEXT DEFAULT ''",
        "avatar": "TEXT DEFAULT ''",
        "profile_complete": "BOOLEAN DEFAULT 0",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))
        connection.execute(text(
            "UPDATE users SET first_name = 'Demo', last_name = 'User', profile_complete = 1 "
            "WHERE lower(email) = 'demo@aegisgrid.local' AND coalesce(profile_complete, 0) = 0"
        ))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
