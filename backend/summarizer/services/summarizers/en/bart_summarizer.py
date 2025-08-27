# summarizer/services/summarizers/en/bart_summarizer.py
# 役割: 英語の既定サマライザー（現時点では Bart）

from transformers import pipeline
from ..base import BaseSummarizer
from ...utils import clean_summary, infer_lang, dynamic_params

class BartSummarizer(BaseSummarizer):
    def __init__(self):
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            tokenizer="facebook/bart-large-cnn",
        )

    def summarize(self, text: str, mode: str = "medium", lang_code: str | None = None) -> str:
        lang = lang_code or "en"
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
