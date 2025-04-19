import argparse
import feedparser
import time
import subprocess
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from pathlib import Path
import pytz

# === Argument Parsing ===
def parse_args():
    parser = argparse.ArgumentParser(description="Generate a Kindle-friendly RSS digest from an OPML file.")
    parser.add_argument("--opml", type=Path, required=True, help="Path to the OPML file containing RSS feeds.")
    parser.add_argument("--email", required=True, help="Your Kindle email address.")
    parser.add_argument("--period", type=int, default=1, help="Number of days back to fetch articles (default: 1)")
    parser.add_argument("--out", type=Path, default=Path.cwd(), help="Directory to save the output HTML (default: current directory)")
    return parser.parse_args()

# === Parse OPML ===
def extract_rss_urls(opml_file):
    tree = ET.parse(opml_file)
    root = tree.getroot()
    return [node.attrib["xmlUrl"] for node in root.iter("outline") if "xmlUrl" in node.attrib]

# === Fetch Articles ===
def fetch_recent_links(feed_url, cutoff_time):
    recent_links = []
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        date_struct = entry.get("published_parsed") or entry.get("updated_parsed")
        if not date_struct:
            continue
        entry_time = datetime.fromtimestamp(time.mktime(date_struct), tz=pytz.UTC)
        if entry_time > cutoff_time and "link" in entry:
            recent_links.append(entry.link)
    return recent_links

# === Run percollate to generate HTML ===
def generate_digest(links, output_file, title):
    if not links:
        print("No articles found in the selected time period.")
        return False
    print(f"Generating HTML digest with {len(links)} articles...")
    cmd = ["percollate", "html", "--toc", "--title", title, "-o", str(output_file)] + links
    subprocess.run(cmd, check=True)
    return True

# === Send via mailx ===
def send_to_kindle(html_file, to_email, title):
    print(f"\nSending '{html_file}' to {to_email}...")
    cmd = ['mailx', '-a', str(html_file), '-s', title, to_email]
    subprocess.run(cmd, input=b'', check=True)

# === Main ===
def main():
    args = parse_args()

    cutoff_time = datetime.now(timezone.utc) - timedelta(days=args.period)
    output_file = args.out / f"kindle_rss_{datetime.now().strftime('%Y-%m-%d')}.html"
    title = "Kindle RSS"

    rss_urls = extract_rss_urls(args.opml)
    print(f"Found {len(rss_urls)} feeds.")

    all_links = []
    for url in rss_urls:
        print(f"Fetching: {url}")
        all_links.extend(fetch_recent_links(url, cutoff_time))

    all_links = list(set(all_links))  # Remove duplicates

    if generate_digest(all_links, output_file, title):
        send_to_kindle(output_file, args.email, title)

if __name__ == "__main__":
    main()
