#!/usr/bin/env python3
"""
Honk Demonlist Scraper
Reads level URLs from data/levels.txt and scrapes stats from
flappy-goose's comment on each Reddit post.
Outputs data/stats.json with per-level data.
"""

import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

BOT_AUTHOR = "flappy-goose"

# Patterns for parsing the bot comment
RE_ATTEMPTS     = re.compile(r'✅\s*([\d,]+)\s*Attempts', re.IGNORECASE)
RE_COMPLETIONS  = re.compile(r'🏆\s*([\d,]+)\s*Completions', re.IGNORECASE)
RE_SUCCESS_RATE = re.compile(r'([\d.]+)%\s*Success Rate', re.IGNORECASE)
# Time before first "by": handles ##.###s or #:##.###
RE_TIME         = re.compile(r'(\d+:\d{2}\.\d+|\d+\.\d+)s?\s+by', re.IGNORECASE)
RE_FIRST_COMP   = re.compile(r'🥇\s*First completion by:\s*(\S+)', re.IGNORECASE)


def fetch_reddit_json(url: str) -> dict:
    """Fetch a Reddit post as JSON using the .json API endpoint."""
    # Normalize URL
    url = url.rstrip("/")
    if not url.endswith(".json"):
        url += ".json"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HonkDemonlistScraper/1.0"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def find_bot_comment(data: list) -> str | None:
    """Recursively search Reddit JSON comment tree for flappy-goose's comment."""
    for listing in data:
        if not isinstance(listing, dict):
            continue
        children = listing.get("data", {}).get("children", [])
        for child in children:
            kind = child.get("kind")
            cdata = child.get("data", {})
            if kind == "t1":
                author = cdata.get("author", "")
                if author.lower() == BOT_AUTHOR.lower():
                    return cdata.get("body", "")
                # Recurse into replies
                replies = cdata.get("replies", {})
                if isinstance(replies, dict):
                    result = find_bot_comment([replies])
                    if result:
                        return result
    return None


def parse_comment(body: str) -> dict:
    """Extract stats from flappy-goose's comment body."""
    stats = {}

    m = RE_ATTEMPTS.search(body)
    if m:
        stats["attempts"] = int(m.group(1).replace(",", ""))

    m = RE_COMPLETIONS.search(body)
    if m:
        stats["completions"] = int(m.group(1).replace(",", ""))

    m = RE_SUCCESS_RATE.search(body)
    if m:
        stats["success_rate"] = float(m.group(1))

    m = RE_TIME.search(body)
    if m:
        stats["fastest_time"] = m.group(1)

    m = RE_FIRST_COMP.search(body)
    if m:
        stats["first_completion"] = m.group(1)

    return stats


def scrape_level(url: str) -> dict:
    """Fetch a Reddit post and return scraped level stats."""
    url = url.strip()
    print(f"  Fetching: {url}")
    data = fetch_reddit_json(url)

    # Get post title
    post_title = data[0]["data"]["children"][0]["data"].get("title", "Unknown Level")

    # Find flappy-goose's comment
    comment_body = find_bot_comment(data)
    if not comment_body:
        print(f"  ⚠️  No flappy-goose comment found for: {post_title}")
        return {
            "url": url.replace(".json", ""),
            "title": post_title,
            "error": "No bot comment found"
        }

    stats = parse_comment(comment_body)
    stats["url"] = url.replace(".json", "")
    stats["title"] = post_title
    print(f"  ✅ {post_title} — {stats.get('success_rate', '?')}% success rate")
    return stats


def main():
    root = Path(__file__).parent.parent
    levels_file = root / "data" / "levels.txt"
    output_file = root / "data" / "stats.json"

    if not levels_file.exists():
        print(f"ERROR: {levels_file} not found.")
        return

    urls = [line.strip() for line in levels_file.read_text().splitlines()
            if line.strip() and not line.startswith("#")]

    print(f"Found {len(urls)} level(s) to scrape.\n")

    results = []
    for i, url in enumerate(urls):
        try:
            result = scrape_level(url)
            results.append(result)
        except Exception as e:
            print(f"  ❌ Error scraping {url}: {e}")
            results.append({"url": url, "error": str(e)})

        # Be polite to Reddit's servers
        if i < len(urls) - 1:
            time.sleep(1.5)

    # Sort by success rate ascending (hardest first) — None/errors go to end
    results.sort(key=lambda x: x.get("success_rate", float("inf")))

    output_file.write_text(json.dumps(results, indent=2))
    print(f"\n✅ Saved stats for {len(results)} level(s) to {output_file}")


if __name__ == "__main__":
    main()
