# Kindle RSS Digest

Generate a daily (or custom period) digest of RSS feed articles from an OPML file, and sends it straight to your kindle device with a clean formatting.

## 🧰 Features

- Parses an OPML file to extract RSS feed URLs
- Fetches only recent articles (within a given number of days)
- Compiles articles into a clean HTML digest using `percollate`
- Sends the digest to your Kindle device via `mailx`

---

## 📦 Requirements

- Python 3.8+
- [`uv`](https://github.com/astral-sh/uv) (for dependency and virtual environment management)
- [`percollate`](https://github.com/danburzo/percollate) (used to generate the HTML digest)
- `mailx` (used to send the email with attachment - you'll need to setup your `.mailrc`)
