"""Fetch and chunk YouTube video transcripts."""

from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url_or_id: str) -> str:
    """Accepts a full YouTube URL (any common format) or a bare video ID."""
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        parsed = urlparse(url_or_id)
        if parsed.hostname == "youtu.be":
            return parsed.path.lstrip("/")
        if "/embed/" in parsed.path or "/shorts/" in parsed.path:
            return parsed.path.rstrip("/").split("/")[-1]
        query_id = parse_qs(parsed.query).get("v")
        if query_id:
            return query_id[0]
        raise ValueError(f"Could not extract a video ID from URL: {url_or_id}")
    return url_or_id


def fetch_transcript(video_id: str) -> str:
    """Returns the full transcript as one plain-text string."""
    try:
        segments = YouTubeTranscriptApi().fetch(video_id)
    except TranscriptsDisabled:
        raise RuntimeError(f"Transcripts are disabled for video '{video_id}'.")
    except NoTranscriptFound:
        raise RuntimeError(f"No transcript found for video '{video_id}'.")
    return " ".join(segment.text for segment in segments)


def chunk_text(text: str, max_chars: int = 3000, overlap: int = 200) -> list[str]:
    """Splits text into overlapping chunks small enough for the summarization
    model's input limit (it caps tokens, so we approximate with characters).
    Overlap keeps a sentence that gets cut at a boundary from losing context.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
