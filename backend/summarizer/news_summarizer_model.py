# backend/summarizer/news_summarizer_model.py
# 役割: 既存コードとの互換レイヤー（実体は services/ 配下に委譲する）

from .services.summarizers import get_summarizer
from .services.utils import infer_lang

def run_summary(text: str, mode: str = "medium", lang_code: str | None = None) -> str:
    """
    互換API:
      旧来の呼び出し元からは run_summary(text, mode, lang_code) を使い続けられる。
      実処理は services/summarizers 配下の各実装に委譲する。
    """
    lang = (lang_code or infer_lang(text) or "en")
    summarizer = get_summarizer(lang)
    return summarizer.summarize(text, mode=mode, lang_code=lang)
