# summarizer/services/summarizers/__init__.py
# 役割: 言語コード→既定サマライザーの割り当てを一元管理する

from .ja.mt5_summarizer import Mt5Summarizer         # 日本語: mt5 を採用
from .en.bart_summarizer import BartSummarizer       # 英語: 既定は Bart
# from .en.led_summarizer import LedSummarizer       # LED に切り替えるならこれを使う

# 既定のインスタンス群（プロセス内で共有）
_SUMMARIZERS = {
    "ja": Mt5Summarizer(),
    "en": BartSummarizer(),   # LED に切り替えるならここを LedSummarizer() に変更
    # "fr": FrenchBartSummarizer(),  # 将来の追加例
}

def get_summarizer(lang: str):
    """言語コードに対応するサマライザーを返す。未対応は 'en' にフォールバックする。"""
    return _SUMMARIZERS.get(lang, _SUMMARIZERS["en"])
