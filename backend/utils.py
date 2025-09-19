import re
import random
import string

def temizle_model_kodlari(baslik: str) -> str:
    if not baslik:
        return ""
    # 3-6 haneli sayıları temizle (ör: model numarası gibi)
    temiz_baslik = re.sub(r'\b\d{3,6}\b(?!\s*(?:[Ll][Ii]|gr|kg|ml|/))', '', baslik)
    temiz_baslik = re.sub(r'\s+', ' ', temiz_baslik).strip()
    if temiz_baslik and not temiz_baslik.lower().startswith("benorra"):
        temiz_baslik = "Benorra " + temiz_baslik
    return temiz_baslik

def rastgele_kod_uret(uzunluk=7):
    karakterler = string.ascii_uppercase + string.digits
    return ''.join(random.choices(karakterler, k=uzunluk))

def kod_uretici(mevcut_kodlar:set, prefix="BNR", uzunluk=7):
    # Güvenli benzersiz kod üretimi
    while True:
        yeni = prefix + rastgele_kod_uret(uzunluk)
        if yeni not in mevcut_kodlar:
            return yeni
