from sqlalchemy.orm import Session
from models import Product
from typing import List, Optional

def get_products(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Product]:
    query = db.query(Product)
    if search:
        search_term = f"%{search}%"
        query = query.filter((Product.urun_adi.ilike(search_term)) | (Product.model_kodu.ilike(search_term)) | (Product.urun_kodu.ilike(search_term)))
    return query.offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_product_by_urun_kodu(db: Session, urun_kodu: str):
    return db.query(Product).filter(Product.urun_kodu == urun_kodu).first()

def create_product(db: Session, urun_kodu: str, urun_adi: str, model_kodu: str):
    p = Product(urun_kodu=urun_kodu, urun_adi=urun_adi, model_kodu=model_kodu)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def update_product(db: Session, product_id: int, urun_adi: str = None, model_kodu: str = None):
    p = get_product_by_id(db, product_id)
    if not p:
        return None
    if urun_adi is not None:
        p.urun_adi = urun_adi
    if model_kodu is not None:
        p.model_kodu = model_kodu
    db.commit()
    db.refresh(p)
    return p

def delete_product(db: Session, product_id: int):
    p = get_product_by_id(db, product_id)
    if not p:
        return None
    db.delete(p)
    db.commit()
    return p

def list_all_model_kodlar(db: Session):
    return [row[0] for row in db.query(Product.model_kodu).all()]
