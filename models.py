import os

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "Doka7744!")
PG_DB = os.getenv("PG_DB", "neto_aiohttp")
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", "5431")

PG_DSN = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"


engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Advertisements(Base):
    __tablename__ = "advs"

    id = Column(Integer, primary_key=True)
    header = Column(String, nullable=False)
    description = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

