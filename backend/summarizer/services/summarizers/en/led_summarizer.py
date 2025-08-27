# summarizer/services/summarizers/led_summarizer.py
from transformers import LEDForConditionalGeneration, LEDTokenizerFast
import torch
from .base import BaseSummarizer
from ..utils import clean_summary

class LEDSummarizer(BaseSummarizer):
    def __init__(self):
        self.model = LEDForConditionalGeneration.from_pretrained("allenai/led-base-16384")
        self.tokenizer = LEDTokenizerFast.from_pretrained("allenai/led-base-16384")

    def summarize(self, text: str, min_new_tokens=120, max_new_tokens=320,
                  no_repeat_ngram_size=4, length_penalty=1.05, repetition_penalty=1.15,
                  num_beams=4) -> str:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=16384)
        global_attention_mask = torch.zeros_like(inputs["attention_mask"])
        global_attention_mask[:, 0] = 1

        summary_ids = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            global_attention_mask=global_attention_mask,
            min_new_tokens=min_new_tokens,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            no_repeat_ngram_size=no_repeat_ngram_size,
            length_penalty=length_penalty,
            repetition_penalty=repetition_penalty,
        )
        return clean_summary(self.tokenizer.decode(summary_ids[0], skip_special_tokens=True))
