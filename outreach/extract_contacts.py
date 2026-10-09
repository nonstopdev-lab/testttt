#!/usr/bin/env python3
"""Collect public Telegram links and contact emails from company websites.

Usage: python3 extract_contacts.py domains.txt output.csv
domains.txt: one domain or URL per line.
"""
import csv, re, ssl, sys
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen

TG_RE = re.compile(r"(?:https?:)?//(?:t|telegram)\.me/([A-Za-z0-9_+]{4,})", re.I)
MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SKIP_TG = {"share", "joinchat", "iv", "addstickers", "proxy", "socks"}
SKIP_MAIL_EXT = (".png", ".jpg", ".svg", ".webp", ".gif", ".js", ".css")
PATHS = ["", "/contact", "/about"]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; contact-research/1.0)"}


def fetch(url):
    try:
        with urlopen(Request(url, headers=HEADERS), timeout=10, context=ssl.create_default_context()) as r:
            return r.read(1_500_000).decode("utf-8", "ignore")
    except Exception:
        return ""


def process(raw):
    base = raw.strip()
    if not base:
        return None
    if not base.startswith("http"):
        base = "https://" + base
    base = base.rstrip("/")
    tg, mails = set(), set()
    for p in PATHS:
        html = fetch(base + p)
        tg |= {m for m in TG_RE.findall(html) if m.lower() not in SKIP_TG}
        mails |= {m for m in MAIL_RE.findall(html) if not m.lower().endswith(SKIP_MAIL_EXT)}
    return {
        "website": base,
        "telegram": " | ".join(f"https://t.me/{t}" for t in sorted(tg)),
        "emails": " | ".join(sorted(mails)[:3]),
    }


def main(src, dst):
    domains = [l for l in open(src) if l.strip()]
    with ThreadPoolExecutor(max_workers=10) as ex:
        rows = [r for r in ex.map(process, domains) if r]
    with open(dst, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["website", "telegram", "emails"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} sites, {sum(1 for r in rows if r['telegram'])} with Telegram")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
