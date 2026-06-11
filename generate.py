import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone

BASE_URL = "https://red.anthropic.com/"
OUTPUT_FILE = "anthropic_red.xml"

def fetch_html(url: str) -> str:
    r = requests.get(url, timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (compatible; rss-bot/1.0)"
    })
    r.raise_for_status()
    return r.text

def extract_articles(html: str):
    soup = BeautifulSoup(html, "html.parser")

    items = []
    seen = set()

    # Generic pass: grab links that look like article/post links.
    # You may need to tune this selector based on the site's HTML.
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        title = a.get_text(" ", strip=True)

        if not href or not title:
            continue

        full_url = urljoin(BASE_URL, href)

        # Keep only site-local links and skip duplicates
        if not full_url.startswith(BASE_URL):
            continue
        if full_url in seen:
            continue

        # Heuristic: likely content pages, not nav/home anchors
        if full_url == BASE_URL:
            continue

        seen.add(full_url)
        items.append({
            "title": title,
            "link": full_url,
            "description": title,
        })

    return items[:30]

def build_feed(items):
    fg = FeedGenerator()
    fg.title("Anthropic Red")
    fg.link(href=BASE_URL)
    fg.description("Unofficial RSS feed generated from red.anthropic.com")
    fg.language("en")
    fg.lastBuildDate(datetime.now(timezone.utc))

    for item in items:
        fe = fg.add_entry()
        fe.title(item["title"])
        fe.link(href=item["link"])
        fe.guid(item["link"], permalink=True)
        fe.description(item["description"])
        fe.pubDate(datetime.now(timezone.utc))

    fg.rss_file(OUTPUT_FILE, pretty=True)

def main():
    html = fetch_html(BASE_URL)
    items = extract_articles(html)
    if not items:
        raise RuntimeError("No articles found. Tune the selectors in generate.py.")
    build_feed(items)
    print(f"Generated {OUTPUT_FILE} with {len(items)} items.")

if __name__ == "__main__":
    main()
