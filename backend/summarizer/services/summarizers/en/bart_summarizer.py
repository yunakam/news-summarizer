# summarizer/services/summarizers/en/bart_summarizer.py
# 役割: 英語の既定サマライザー（Bart, 長文は分割対応版）

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
        self.max_input_tokens = 1000  # 安全のため 1024 より少し下げる
        self.window_chars = 80        # 文末探索の許容範囲（文字数単位）

    def _smart_split(self, text: str):
        """
        長文を BART の許容長以下に分割。
        なるべく文の途中で切らない（.優先, なければ,）。
        """
        tokens = self.summarizer.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + self.max_input_tokens, len(tokens))
            sub_text = self.summarizer.tokenizer.decode(tokens[start:end])

            # "." の位置を探す
            cut_idx = sub_text.rfind(".")
            if cut_idx == -1 or (len(sub_text) - cut_idx) > self.window_chars:
                # "," の位置を探す
                cut_idx = sub_text.rfind(",")

            if cut_idx == -1 or (len(sub_text) - cut_idx) > self.window_chars:
                cut_idx = len(sub_text)

            chunk = sub_text[: cut_idx + 1]
            chunks.append(chunk)

            # 次の開始位置を更新
            start = start + len(self.summarizer.tokenizer.encode(chunk, add_special_tokens=False))

        return chunks

    def _summarize_chunk(self, text: str, mode: str, lang: str):
        n_in = len(self.summarizer.tokenizer.encode(text, add_special_tokens=False))
        params = dynamic_params(n_in, mode, lang_code=lang, text=text)

        print(f"[Chunk] input={n_in}, min_new={params['min_new_tokens']}, max_new={params['max_new_tokens']}")

        out = self.summarizer(
            text,
            do_sample=False,
            num_beams=4,
            truncation=True,
            repetition_penalty=1.1,
            **params,
        )
        return clean_summary(out[0]["summary_text"])

    def summarize(self, text: str, mode: str = "medium", lang_code: str | None = None) -> str:
        lang = lang_code or "en"
        n_in = len(self.summarizer.tokenizer.encode(text, add_special_tokens=False))

        if n_in <= self.max_input_tokens:
            # ログ出力
            params = dynamic_params(n_in, mode, lang_code=lang, text=text)
            self.log_summary_info(lang, mode, n_in,
                                params["min_new_tokens"], params["max_new_tokens"])
            return self._summarize_chunk(text, mode, lang)
        
        else:
            # 1. チャンクごとに要約
            chunks = self._smart_split(text)
            partial_summaries = [self._summarize_chunk(ch, mode, lang) for ch in chunks]

            # 2. 部分要約を結合して再要約（shortモードでまとめ）
            combined = " ".join(partial_summaries)
            return self._summarize_chunk(combined, "short", lang)
