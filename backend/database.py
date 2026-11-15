from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Пока используем SQLite для локальной разработки
# Позже заменим на PostgreSQL через переменную окружения
DATABASE_URL = "sqlite:///./sprint_planner.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Генератор сессии БД для FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()