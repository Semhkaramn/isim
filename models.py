from sqlalchemy import Column, String, Integer, DateTime, func
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    urun_kodu = Column(String, unique=True, index=True, nullable=False)
    urun_adi = Column(String, nullable=False)
    model_kodu = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
