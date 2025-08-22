#!/usr/bin/env python

from transformers import pipeline

_summarizer_ja = pipeline(
    "summarization",
    model="tsmatz/mt5_summarize_japanese",
    tokenizer="tsmatz/mt5_summarize_japanese",
    device_map="auto",   # GPUがあれば自動利用（なければCPU）
)

def run_summary_ja(text: str, mode: str ="medium") -> str:
    if mode == "short":
        params = dict(min_new_tokens=10, max_new_tokens=50, length_penalty=0.9)
    elif mode == "medium":
        params = dict(min_new_tokens=50, max_new_tokens=300, length_penalty=1.1)
    elif mode == "long":
        params = dict(min_new_tokens=80, max_new_tokens=500, length_penalty=1.3)
    else:
        raise ValueError("Mode value invalid - must be short/medium/long")

    out = _summarizer_ja(
        text,
        do_sample=False,
        num_beams=4,
        truncation=True,
        no_repeat_ngram_size=3,
        repetition_penalty=1.1,
        **params
    )
    return out[0]["summary_text"]
