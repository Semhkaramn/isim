import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import io

from database import SessionLocal, engine, Base
import models, crud
from gpt_service import gpt_seo_baslik
from utils import kod_uretici

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ürün Yönetim Sistemi")

# CORS - frontend origin ekle (local için *)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production: frontend origin ile sınırla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health
@app.get("/health")
def health():
    return {"status": "ok"}

# List products
@app.get("/products")
def list_products(skip: int = 0, limit: int = 100, search: str = Query(None), db: Session = Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit, search=search)

# Get single
@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = crud.get_product_by_id(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return p

# Create product
@app.post("/products")
def add_product(urun_kodu: str, urun_adi: str, db: Session = Depends(get_db)):
    # if exists, update
    existing = crud.get_product_by_urun_kodu(db, urun_kodu)
    if existing:
        raise HTTPException(status_code=400, detail="Ürün kodu zaten mevcut")
    mevcut_model_kodlar = set(crud.list_all_model_kodlar(db))
    model_kodu = kod_uretici(mevcut_model_kodlar)
    seo_baslik = gpt_seo_baslik(urun_adi)
    return crud.create_product(db, urun_kodu, seo_baslik, model_kodu)

# Update product
@app.put("/products/{product_id}")
def update_product(product_id: int, urun_adi: str = None, model_kodu: str = None, db: Session = Depends(get_db)):
    seo_baslik = None
    if urun_adi:
        seo_baslik = gpt_seo_baslik(urun_adi)
    updated = crud.update_product(db, product_id, urun_adi=seo_baslik, model_kodu=model_kodu)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

# Delete
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}

# Upload Excel/CSV
@app.post("/upload")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read()
    try:
        if file.filename.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        else:
            df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Dosya okunamadı: {e}")

    added = 0
    errors = []
    mevcut_model_kodlar = set(crud.list_all_model_kodlar(db))
    for idx, row in df.iterrows():
        urun_kodu = str(row.get("URUNKODU") or row.get("urun_kodu") or "").strip()
        urun_adi = str(row.get("ADI") or row.get("urun_adi") or "").strip()
        if not urun_kodu or not urun_adi:
            errors.append({"row": int(idx)+1, "reason": "urun_kodu veya urun_adi eksik"})
            continue
        if crud.get_product_by_urun_kodu(db, urun_kodu):
            # skip duplicate
            continue
        model_kodu = kod_uretici(mevcut_model_kodlar)
        mevcut_model_kodlar.add(model_kodu)
        seo_baslik = gpt_seo_baslik(urun_adi)
        try:
            crud.create_product(db, urun_kodu, seo_baslik, model_kodu)
            added += 1
        except Exception as e:
            errors.append({"row": int(idx)+1, "reason": str(e)})
    return {"added": added, "errors": errors}

# Download CSV
@app.get("/download")
def download_all(db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=0, limit=10000)
    import csv, io
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["id","urun_kodu","urun_adi","model_kodu","created_at","updated_at"])
    for p in products:
        writer.writerow([p.id, p.urun_kodu, p.urun_adi, p.model_kodu, p.created_at, p.updated_at])
    return {"csv": out.getvalue()}
