# summarizer/services/utils.py
# 役割: クリーニング、言語推定、出力長ダイナミクス等の共通ユーティリティ

import re
import unicodedata
from math import ceil

# ---- 出力のクリーンアップ（既存実装を移植）----
def clean_summary(text: str) -> str:
    if not text:
        return text
    s = unicodedata.normalize("NFKC", text)
    s = re.sub(r"\s*<\s*n\s*>\s*", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*[\[\]\{\}\|]{2,}\s*", " ", s)
    s = re.sub(r"\s*<{2,}\s*|>{2,}\s*", " ", s)
    s = re.sub(r"\s+([,.:;!?%])", r"\1", s)
    s = re.sub(r":(\"|')", r": \1", s)
    s = re.sub(r"([(\[\{])\s+", r"\1", s)
    s = re.sub(r"\s+([)\]\}])", r"\1", s)
    s = re.sub(r"\s{2,}([\"'])", r" \1", s)
    s = re.sub(r"([\"'])\s{2,}", r"\1 ", s)
    s = re.sub(r"([\.!?]){3,}", r"\1\1", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

# ---- 文字スクリプトからの言語推定（既存実装を移植）----
_CJK_RE = re.compile(r"[\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]")
_ZH_RE  = re.compile(r"[\u4E00-\u9FFF]")
_JA_RE  = re.compile(r"[\u3040-\u30FF]")
_KO_RE  = re.compile(r"[\uAC00-\uD7AF]")
_TH_RE  = re.compile(r"[\u0E00-\u0E7F]")
_LO_RE  = re.compile(r"[\u0E80-\u0EFF]")
_KM_RE  = re.compile(r"[\u1780-\u17FF]")
_MY_RE  = re.compile(r"[\u1000-\u109F]")

def infer_lang(text: str) -> str | None:
    if _JA_RE.search(text): return "ja"
    if _KO_RE.search(text): return "ko"
    if _ZH_RE.search(text): return "zh"
    if _TH_RE.search(text): return "th"
    if _LO_RE.search(text): return "lo"
    if _KM_RE.search(text): return "km"
    if _MY_RE.search(text): return "my"
    if _CJK_RE.search(text): return "zh"
    return None

# ---- 言語別プロファイル（既存実装を要約）----
DEFAULT_PROFILE = {
    "ratio":  {"short": (0.11, 0.18), "medium": (0.18, 0.28), "long": (0.28, 0.43)},
    "cap":    {"short": (40, 220),    "medium": (120, 380),   "long": (190, 620)},
    "no_repeat": 3,
    "length_penalty": {"short": 1.0, "medium": 1.05, "long": 1.2},
}
SPECIAL_LANG_PROFILES = {
    "ja": {
        "ratio":  {"short": (0.12, 0.18), "medium": (0.15, 0.25), "long": (0.25, 0.40)},
        "cap":    {"short": (50, 150),    "medium": (100, 320),   "long": (160, 520)},
        "no_repeat": 3,
        "length_penalty": {"short": 1.0, "medium": 1.05, "long": 1.2},
    },
    "zh": {
        "ratio":  {"short": (0.08, 0.12), "medium": (0.12, 0.20), "long": (0.20, 0.35)},
        "cap":    {"short": (40, 130),    "medium": (85, 260),    "long": (140, 420)},
        "no_repeat": 4,
        "length_penalty": {"short": 1.0, "medium": 1.05, "long": 1.2},
    },
    "ko": {
        "ratio":  {"short": (0.10, 0.16), "medium": (0.14, 0.23), "long": (0.23, 0.38)},
        "cap":    {"short": (50, 145),    "medium": (95, 290),    "long": (150, 470)},
        "no_repeat": 3,
        "length_penalty": {"short": 1.0, "medium": 1.05, "long": 1.2},
    },
    # （th / lo / km / my も必要に応じて追加）
}

def _pick_profile(lang_code: str | None = None, text: str | None = None):
    code = (lang_code or "").lower()
    if code in SPECIAL_LANG_PROFILES:
        return SPECIAL_LANG_PROFILES[code]
    if text:
        from .utils import infer_lang as _infer  # 循環回避のための遅延参照ではなく実体は同一
    return SPECIAL_LANG_PROFILES.get(infer_lang(text), DEFAULT_PROFILE) if text else DEFAULT_PROFILE

def _target_len_by_ratio(n_in: int, mode: str, prof: dict) -> int:
    lo, hi = prof["ratio"][mode]
    cap_lo, cap_hi = prof["cap"][mode]
    target = int(n_in * ((lo + hi) / 2))
    return max(cap_lo, min(target, cap_hi))

def dynamic_params(n_in_tokens: int, mode: str, lang_code: str | None = None, text: str | None = None):
    """入力長・言語・モードから min/max_new_tokens 等を算出する。"""
    prof = SPECIAL_LANG_PROFILES.get(lang_code, _pick_profile(lang_code, text))
    target = _target_len_by_ratio(n_in_tokens, mode, prof)
    min_new = max(10, int(target * 0.8))
    max_new = max(min_new + 10, target)
    return {
        "min_new_tokens": min_new,
        "max_new_tokens": max_new,
        "length_penalty": prof["length_penalty"][mode],
        "no_repeat_ngram_size": prof["no_repeat"],
    }
