"""CLI entry point: YouTube video -> transcript -> chunked summary -> bullets."""

import argparse
import re
import sys

from transcript import extract_video_id, fetch_transcript, chunk_text
from summarize import summarize_chunks


def to_bullets(summary: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", summary.strip())
    return [s.strip() for s in sentences if s.strip()]


def main():
    parser = argparse.ArgumentParser(description="Summarize a YouTube video's transcript.")
    parser.add_argument("video", help="YouTube URL or video ID")
    args = parser.parse_args()

    video_id = extract_video_id(args.video)

    print(f"Fetching transcript for video '{video_id}'...")
    try:
        text = fetch_transcript(video_id)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    chunks = chunk_text(text)
    print(f"Transcript split into {len(chunks)} chunk(s). Summarizing...")

    summary = summarize_chunks(chunks)

    print("\nSummary:")
    for bullet in to_bullets(summary):
        print(f"- {bullet}")


if __name__ == "__main__":
    main()
