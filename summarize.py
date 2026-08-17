"""Summarize text with a local Hugging Face summarization model.

Loads the tokenizer/model directly (tokenize -> generate -> decode) rather
than using the `pipeline("summarization", ...)` shortcut, since that
shortcut was removed in transformers 5.x.
"""

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

_tokenizer = None
_model = None


def get_model():
    """Loads the tokenizer/model once and reuses them (loading is the slow part)."""
    global _tokenizer, _model
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    return _tokenizer, _model


def summarize_chunk(text: str, max_length: int = 130, min_length: int = 30) -> str:
    tokenizer, model = get_model()
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    output_ids = model.generate(
        **inputs, max_length=max_length, min_length=min_length, num_beams=4
    )
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)


def summarize_chunks(chunks: list[str]) -> str:
    """Map-reduce summarization: summarize each chunk, then summarize the
    combined chunk summaries into one final summary. Skips the reduce step
    if there was only one chunk to begin with.
    """
    chunk_summaries = [summarize_chunk(chunk) for chunk in chunks]

    if len(chunk_summaries) == 1:
        return chunk_summaries[0]

    combined = " ".join(chunk_summaries)
    return summarize_chunk(combined, max_length=200, min_length=60)
