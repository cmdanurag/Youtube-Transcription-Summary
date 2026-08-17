"""Fetch and chunk YouTube video transcripts."""

import os
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    RequestBlocked,
    TranscriptsDisabled,
    NoTranscriptFound,
)
from youtube_transcript_api.proxies import WebshareProxyConfig

load_dotenv()


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


def _get_proxy_config():
    """Builds a Webshare proxy config from env vars, if credentials are set.
    Falls back to None (direct connection), which risks YouTube's IP blocks.
    """
    username = os.environ.get("WEBSHARE_PROXY_USERNAME")
    password = os.environ.get("WEBSHARE_PROXY_PASSWORD")
    if username and password:
        return WebshareProxyConfig(proxy_username=username, proxy_password=password)
    return None


def fetch_transcript(video_id: str) -> str:
    """Returns the full transcript as one plain-text string."""
    try:
        api = YouTubeTranscriptApi(proxy_config=_get_proxy_config())
        segments = api.fetch(video_id)
    except TranscriptsDisabled:
        raise RuntimeError(f"Transcripts are disabled for video '{video_id}'.")
    except NoTranscriptFound:
        raise RuntimeError(f"No transcript found for video '{video_id}'.")
    except RequestBlocked:
        raise RuntimeError(
            "YouTube is blocking requests from this IP. Set WEBSHARE_PROXY_USERNAME "
            "and WEBSHARE_PROXY_PASSWORD in your .env file to route through a proxy "
            "(see README), or wait and try again later."
        )
    except CouldNotRetrieveTranscript as e:
        raise RuntimeError(f"Could not retrieve a transcript for '{video_id}': {e}")
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
