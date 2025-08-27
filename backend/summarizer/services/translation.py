# 何をするか：DeepL API（Free）で翻訳する安全なラッパー
import os, time, hashlib, requests
from django.core.cache import cache

DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY", "")
DEEPL_BASE = "https://api-free.deepl.com/v2"

class TranslationError(Exception): pass

def deepl_translate(text: str, src: str | None, tgt: str) -> str:
    if not DEEPL_API_KEY:
        raise TranslationError("DEEPL_API_KEY が未設定である。")

    # シンプルなキャッシュ（24h）
    key = f"deepl:{hashlib.md5((src or '').encode()+tgt.encode()+text.encode()).hexdigest()}"
    cached = cache.get(key)
    if cached: 
        return cached

    data = {"auth_key": DEEPL_API_KEY, "text": text, "target_lang": tgt.upper()}
    if src:
        data["source_lang"] = src.upper()

    for attempt in range(3):
        r = requests.post(f"{DEEPL_BASE}/translate", data=data, timeout=60)
        if r.status_code == 200:
            out = r.json()["translations"][0]["text"]
            cache.set(key, out, 60*60*24)
            return out
        if r.status_code in (429, 503):
            time.sleep(2 * (attempt + 1))
            continue
        raise TranslationError(f"DeepL API エラー: {r.status_code} {r.text}")

    raise TranslationError("DeepL リトライ上限に到達した。")
