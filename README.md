# YouTube Video Summarizer

Pulls a YouTube video's transcript, splits it into chunks, summarizes it with
a local Hugging Face model, and prints a bulleted summary.

## How it works

1. **Transcript** — [transcript.py](transcript.py) pulls captions via
   `youtube-transcript-api` and joins them into one block of text.
2. **Chunking** — the transcript is split into overlapping chunks, because
   the summarization model can only read a limited number of tokens at once.
3. **Map-reduce summarization** — [summarize.py](summarize.py) summarizes
   each chunk separately (the "map" step), then summarizes those summaries
   together into one final summary (the "reduce" step).
4. **Output** — [main.py](main.py) splits the final summary into sentences
   and prints each as a bullet.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Usage

```powershell
.venv\Scripts\python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Also accepts a bare video ID, a `youtu.be/...` link, or a `/shorts/...` link.

The first run downloads the summarization model
(`sshleifer/distilbart-cnn-12-6`, ~300MB) and caches it locally, so it's
one-time cost — later runs start faster.

## Notes

- Videos with disabled or missing captions will raise a clear error instead
  of crashing.
- The model, chunk size, and summary length are all adjustable constants at
  the top of [summarize.py](summarize.py) and [transcript.py](transcript.py).

## If YouTube blocks your IP

`youtube-transcript-api` works by scraping the video page rather than using
an official API, so YouTube sometimes blocks the requesting IP after enough
calls (you'll see an `IpBlocked`/`RequestBlocked` error). Fixes, in order of
effort:

1. Wait — blocks are often temporary.
2. Route requests through a proxy: copy `.env.example` to `.env`, sign up at
   [Webshare](https://www.webshare.io/) and purchase a "Residential" proxy
   package (not "Proxy Server" or "Static Residential"), then fill in
   `WEBSHARE_PROXY_USERNAME` and `WEBSHARE_PROXY_PASSWORD` in `.env` with the
   credentials from your [Webshare proxy settings](https://dashboard.webshare.io/proxy/settings).
   The script picks these up automatically via `python-dotenv`.
