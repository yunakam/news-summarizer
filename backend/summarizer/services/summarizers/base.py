# summarizer/services/summarizers/base.py
from abc import ABC, abstractmethod

class BaseSummarizer(ABC):
    @abstractmethod
    def summarize(self, text: str, **kwargs) -> str:
        """各モデルで必ず実装するインターフェース"""
        pass

    def log_summary_info(self, lang: str, mode: str, n_in: int,
                         min_new: int, max_new: int) -> None:
        """サマライザー共通のログ出力"""
        print(f"Summarizing with {lang} ...\n")
        print(f"Applied mode: {mode}")
        print(f"input token: {n_in} -> min_new_tokens:{min_new}/max_new_tokens:{max_new}")
