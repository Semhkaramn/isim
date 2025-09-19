import os
import time
import openai
from utils import temizle_model_kodlari

openai.api_key = os.getenv("OPENAI_API_KEY")

DEFAULT_TIMEOUT = 30

def _make_prompt(urun_adi: str) -> str:
    return f"""
Aşağıdaki ürün adı için:
- Ürün başlığından marka ismini ve ürün kodunu çıkar.
- Sadece ürünün ana özelliğini yansıtan, etkileyici, kısa, akılda kalıcı ve SEO uyumlu bir başlık üret.
- Başlık 6-7 kelimeyi geçmesin.

Başlık: [Yeni SEO Başlık]
Ürün: "{urun_adi}"
"""

def gpt_seo_baslik(urun_adi: str, retries: int = 3, delay: int = 3) -> str:
    if not urun_adi:
        return ""
    prompt = _make_prompt(urun_adi)
    for attempt in range(retries):
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen profesyonel bir seo uzmanısın"},
                    {"role": "user", "content": prompt},
                ],
                timeout=DEFAULT_TIMEOUT
            )
            text = resp.choices[0].message.content.strip()
            # Beklenen formatta "Başlık: ..." satırı dönerse çek
            for line in text.splitlines():
                if line.lower().strip().startswith("başlık:"):
                    baslik = line.split(":", 1)[1].strip().strip('"')
                    return temizle_model_kodlari(baslik)
            # yoksa tüm yanıtı temizle
            return temizle_model_kodlari(text)
        except Exception as e:
            print(f"[gpt_service] Hata (deneme {attempt+1}/{retries}): {e}")
            time.sleep(delay)
    # fallback
    return temizle_model_kodlari(urun_adi)
