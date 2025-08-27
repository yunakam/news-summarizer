# 入力言語に応じて要約前/後の翻訳ルートを決め、要約を実行する
from .translation import deepl_translate, TranslationError
from summarizer.news_summarizer_model import run_summary, infer_lang  # 既存を利用

PIVOT_DEFAULT = "en"   # 既定ピボットは英語
PIVOT_FOR_KO  = "ja"   # 特例：韓国語は日本語にピボット

def route_and_summarize(raw_text: str, target_lang: str, length_mode: str = "medium") -> dict:
    """
    戻り値: {"detected": str, "pivoted": bool, "summary_src": str, "summary": str}
    """
    detected = infer_lang(raw_text) or "en"

    # ルーティング決定（ko だけ ja にピボット）
    if detected in {"en", "ja"}:
        text_for_sum = raw_text
        summary_src  = detected
        pivoted = False
    else:
        pivot_lang = PIVOT_FOR_KO if detected == "ko" else PIVOT_DEFAULT
        text_for_sum = deepl_translate(raw_text, src=detected, tgt=pivot_lang)
        print(f"Original text translated into {pivot_lang}")
        summary_src  = pivot_lang
        pivoted = True

    # 要約の実行（英/日モデルは news_summarizer_model.py 側で定義済み）
    summary_native = run_summary(text_for_sum, mode=length_mode, lang_code=summary_src)

    # 最終翻訳（ユーザー指定言語に合わせる）
    if target_lang and target_lang.lower() != summary_src.lower():
        summary_out = deepl_translate(summary_native, src=summary_src, tgt=target_lang)
    else:
        summary_out = summary_native

    return {
        "detected": detected,   # detected source lang
        "pivoted": pivoted,     # whether it was pivoted: True/False
        "summary_src": summary_src, # lang used for summarization: en/ja
        "summary": summary_out, # summary result in the designated target lang
    }
