# summarizer/services/summarizers/ja/mt5_summarizer.py
# 役割: 日本語の既定サマライザー（mt5）を提供する

from transformers import pipeline
from ..base import BaseSummarizer
from ...utils import clean_summary, infer_lang, dynamic_params

class Mt5Summarizer(BaseSummarizer):
    def __init__(self):
        self.summarizer = pipeline(
            "summarization",
            model="tsmatz/mt5_summarize_japanese",
            tokenizer="tsmatz/mt5_summarize_japanese",
        )

    def summarize(self, text: str, mode: str = "medium", lang_code: str | None = None) -> str:
        lang = lang_code or infer_lang(text) or "ja"
        n_in = len(self.summarizer.tokenizer.encode(text, add_special_tokens=False))
        params = dynamic_params(n_in, mode, lang_code=lang, text=text)
        out = self.summarizer(
            text,
            do_sample=False,
            num_beams=4,
            truncation=True,
            repetition_penalty=1.1,
            **params
        )
        return clean_summary(out[0]["summary_text"])
