#!/usr/bin/env python

from transformers import pipeline
import re
import unicodedata
# from langchain.llms import HuggingFacePipeline
# from langchain.prompts import PromptTemplate
# from langchain_huggingface.llms import HuggingFacePipeline
# from langchain_core.prompts import PromptTemplate


# 入力テキストの長さによって出力トークン数をダイナミックに設定する
from math import ceil

# 言語ごとに適切な圧縮率レンジと上限キャップを指定

# ----  汎用デフォルト（空白区切り系を想定：英/独/仏/西/アラビア語 等） ----
DEFAULT_PROFILE = {
    "ratio":  {"short": (0.11, 0.18), "medium": (0.18, 0.28), "long": (0.28, 0.43)},
    "cap":    {"short": (40, 190),    "medium": (120, 380),   "long": (190, 620)},
    "no_repeat": 3,
    "length_penalty": {"short": 0.9, "medium": 1.05, "long": 1.2},
}

# ---- 特殊レンジ・キャップが要る言語だけを個別定義 ----
SPECIAL_LANG_PROFILES = {
    # 日本語
    "ja": {
        "ratio":  {"short": (0.08, 0.15), "medium": (0.15, 0.25), "long": (0.25, 0.40)},
        "cap":    {"short": (32, 160),    "medium": (100, 320),   "long": (160, 520)},
        "no_repeat": 3,
        "length_penalty": {"short": 0.9, "medium": 1.05, "long": 1.2},
    },
    # 中国語（簡/繁共通）
    "zh": {
        "ratio":  {"short": (0.05, 0.12), "medium": (0.12, 0.20), "long": (0.20, 0.35)},
        "cap":    {"short": (28, 130),    "medium": (85, 260),    "long": (140, 420)},
        "no_repeat": 4,
        "length_penalty": {"short": 0.9, "medium": 1.05, "long": 1.2},
    },
    # 韓国語
    "ko": {
        "ratio":  {"short": (0.07, 0.14), "medium": (0.14, 0.23), "long": (0.23, 0.38)},
        "cap":    {"short": (30, 145),    "medium": (95, 290),    "long": (150, 470)},
        "no_repeat": 3,
        "length_penalty": {"short": 0.9, "medium": 1.05, "long": 1.2},
    },
    # 分かち書きが乏しいスクリプト系（タイ/ラオス/クメール/ビルマなど）
    # モデル依存で重複が出やすいので no_repeat=4、比率はCJK寄りにやや低め
    "th": {
        "ratio":  {"short": (0.07, 0.14), "medium": (0.14, 0.22), "long": (0.22, 0.36)},
        "cap":    {"short": (30, 145),    "medium": (95, 280),    "long": (150, 450)},
        "no_repeat": 4,
        "length_penalty": {"short": 0.9, "medium": 1.05, "long": 1.2},
    },
    "lo": {  # Lao
        "ratio":  {"short": (0.07, 0.14), "medium": (0.14, 0.22), "long": (0.22, 0.36)},
        "cap":    {"short": (30, 145),    "medium": (95, 280),    "long": (150, 450)},
        "no_repeat": 4,
        "length_penalty": {"short": 0.9, "medium": 1.05, "long": 1.2},
    },
    "km": {  # Khmer
        "ratio":  {"short": (0.07, 0.14), "medium": (0.14, 0.22), "long": (0.22, 0.36)},
        "cap":    {"short": (30, 145),    "medium": (95, 280),    "long": (150, 450)},
        "no_repeat": 4,
        "length_penalty": {"short": 0.9, "medium": 1.05, "long": 1.2},
    },
    "my": {  # Burmese
        "ratio":  {"short": (0.07, 0.14), "medium": (0.14, 0.22), "long": (0.22, 0.36)},
        "cap":    {"short": (30, 145),    "medium": (95, 280),    "long": (150, 450)},
        "no_repeat": 4,
        "length_penalty": {"short": 0.9, "medium": 1.05, "long": 1.2},
    },
}


# 文字スクリプトからの言語推定
_CJK_RE = re.compile(r"[\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]")
_ZH_RE  = re.compile(r"[\u4E00-\u9FFF]")      # 漢字のみが多ければ zh 寄せ
_JA_RE  = re.compile(r"[\u3040-\u30FF]")      # かなを含めば ja
_KO_RE  = re.compile(r"[\uAC00-\uD7AF]")      # ハングル音節
_TH_RE  = re.compile(r"[\u0E00-\u0E7F]")      # タイ
_LO_RE  = re.compile(r"[\u0E80-\u0EFF]")      # ラオ
_KM_RE  = re.compile(r"[\u1780-\u17FF]")      # クメール
_MY_RE  = re.compile(r"[\u1000-\u109F]")      # ビルマ

def infer_lang(text: str) -> str | None:
    if _JA_RE.search(text): return "ja"
    if _KO_RE.search(text): return "ko"
    if _ZH_RE.search(text): return "zh"
    if _TH_RE.search(text): return "th"
    if _LO_RE.search(text): return "lo"
    if _KM_RE.search(text): return "km"
    if _MY_RE.search(text): return "my"
    if _CJK_RE.search(text): return "zh"  # フォールバックで zh
    return None

# プロファイルの選択ロジック
def pick_profile(lang_code: str | None = None, text: str | None = None):
    code = (lang_code or "").lower()
    if code in SPECIAL_LANG_PROFILES:
        return SPECIAL_LANG_PROFILES[code]

    # lang_code が無い・未知の場合は`infer_lang_from_script`で推定
    if text:
        inferred = infer_lang(text)
        if inferred and inferred in SPECIAL_LANG_PROFILES:
            return SPECIAL_LANG_PROFILES[inferred]

    # どれにも当てはまらなければ汎用デフォルト
    return DEFAULT_PROFILE


# 既存のダイナミックパラメータ関数をプロファイル対応に
def _target_len_by_ratio(n_in: int, mode: str, prof: dict) -> int:
    lo, hi = prof["ratio"][mode]
    cap_lo, cap_hi = prof["cap"][mode]
    target = int(n_in * ((lo + hi) / 2))
    return max(cap_lo, min(target, cap_hi))

def dynamic_params(
    n_in_tokens: int,   # 入力のトークン数
    mode: str,          # "short" / "medium" / "long" のいずれか
    lang_code: str | None = None,  # 言語コード
    text: str | None = None        # 要約する入力テキスト→言語推定にも使う
):
    prof = pick_profile(lang_code, text)
    target = _target_len_by_ratio(n_in_tokens, mode, prof)
    min_new = max(10, int(target * 0.6))
    max_new = max(min_new + 10, target)
    return {
        "min_new_tokens": min_new,
        "max_new_tokens": max_new,
        "length_penalty": prof["length_penalty"][mode],
        "no_repeat_ngram_size": prof["no_repeat"],
    }


_summarizer_ja = pipeline(
    "summarization",
    model="tsmatz/mt5_summarize_japanese",
    tokenizer="tsmatz/mt5_summarize_japanese",
)

# 言語ごとの summarizerパイプライン
_summarizers = {
    # 日本語モデル
    "ja": pipeline(
        "summarization",
        model="tsmatz/mt5_summarize_japanese",
        tokenizer="tsmatz/mt5_summarize_japanese",
    ),
    # 英語用モデル
    "en": pipeline(
        "summarization",
        model="google/bigbird-pegasus-large-arxiv",
        tokenizer="google/bigbird-pegasus-large-arxiv",
    ),
}


# 出力のクリーンアップ
def clean_summary(text: str) -> str:
    if not text:
        return text

    # Unicode正規化（全角/半角・合成文字などの揺れを抑える）
    s = unicodedata.normalize("NFKC", text)

    # <n> -> 改行
    s = re.sub(r"\s*<\s*n\s*>\s*", "\n", s, flags=re.IGNORECASE)
    # 学習ノイズ記号を削除
    s = re.sub(r"\s*[\[\]\{\}\|]{2,}\s*", " ", s)
    s = re.sub(r"\s*<{2,}\s*|>{2,}\s*", " ", s)

    # 句読点前スペース削除
    s = re.sub(r"\s+([,.:;!?%])", r"\1", s)

    # コロン直後の引用符にスペースを入れる:  says:"the -> says: "the
    s = re.sub(r":(\"|')", r": \1", s)

    # 開く括弧の直後や閉じる括弧の直前の余分なスペース
    s = re.sub(r"([(\[\{])\s+", r"\1", s)
    s = re.sub(r"\s+([)\]\}])", r"\1", s)

    # 引用符の前後の余分なスペース
    s = re.sub(r"\s+([\"'])", r"\1", s)
    s = re.sub(r"([\"'])\s+", r"\1", s)

    # ピリオド重複・句点の連続を軽減（……等を壊さない範囲で）
    s = re.sub(r"([\.!?]){3,}", r"\1\1", s)

    # 連続空白・連続改行の縮約
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)

    # 先頭/末尾のホワイトスペース除去
    s = s.strip()

    return s


def run_summary(text: str, mode: str = "medium", lang_code: str | None = None):
    # 言語コードが無ければ推定
    lang = lang_code or infer_lang(text)
    if lang not in _summarizers:
        lang = "en"  # 未対応言語はデフォルト英語にフォールバック
    print("Original text language: ", lang)

    summarizer = _summarizers[lang]

    # 入力トークン数の算出（tokenizer は summarizer から取得）
    n_in = len(summarizer.tokenizer.encode(text, add_special_tokens=False))

    # 言語 + モードに応じてパラメータ算出
    params = dynamic_params(n_in, mode, lang_code=lang, text=text)

    # サマリ生成
    out = summarizer(
        text,
        do_sample=False,
        num_beams=4,
        truncation=True,
        repetition_penalty=1.1,
        **params
    )
    raw =  out[0]["summary_text"]
    return clean_summary(raw)
