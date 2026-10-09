#!/usr/bin/env python3
"""Collect public Telegram links and contact emails from company websites.

Usage: python3 extract_contacts.py domains.txt output.csv [--js]
domains.txt: one domain or URL per line.

--js  re-check sites that showed no Telegram link in their static HTML by
      rendering them in headless Chromium (needs: pip install playwright).
"""
import csv, os, re, ssl, sys
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


def parse(html, tg, mails):
    tg |= {m for m in TG_RE.findall(html) if m.lower() not in SKIP_TG}
    mails |= {m for m in MAIL_RE.findall(html) if not m.lower().endswith(SKIP_MAIL_EXT)}


def normalize(raw):
    base = raw.strip()
    if not base:
        return None
    if not base.startswith("http"):
        base = "https://" + base
    return base.rstrip("/")


def row(base, tg, mails):
    return {
        "website": base,
        "telegram": " | ".join(f"https://t.me/{t}" for t in sorted(tg)),
        "emails": " | ".join(sorted(mails)[:3]),
    }


def process(raw):
    base = normalize(raw)
    if not base:
        return None
    tg, mails = set(), set()
    for p in PATHS:
        parse(fetch(base + p), tg, mails)
    return row(base, tg, mails)


def render_pass(rows):
    """Re-check rows with no Telegram link using a real browser."""
    from playwright.sync_api import sync_playwright

    todo = [r for r in rows if not r["telegram"]]
    if not todo:
        return
    kwargs = {}
    exe = os.environ.get("CHROMIUM_PATH")
    if exe:
        kwargs["executable_path"] = exe
    with sync_playwright() as pw:
        browser = pw.chromium.launch(**kwargs)
        ctx = browser.new_context(user_agent=HEADERS["User-Agent"])
        for r in todo:
            tg, mails = set(), set()
            for p in PATHS:
                page = ctx.new_page()
                try:
                    page.goto(r["website"] + p, wait_until="networkidle", timeout=20000)
                    page.wait_for_timeout(1500)
                    hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
                    parse(page.content() + "\n" + "\n".join(hrefs), tg, mails)
                except Exception:
                    pass
                finally:
                    page.close()
            if tg:
                r["telegram"] = row(r["website"], tg, set())["telegram"]
            if mails and not r["emails"]:
                r["emails"] = row(r["website"], set(), mails)["emails"]
        browser.close()


def main(src, dst, use_js):
    domains = [l for l in open(src) if l.strip()]
    with ThreadPoolExecutor(max_workers=10) as ex:
        rows = [r for r in ex.map(process, domains) if r]
    if use_js:
        render_pass(rows)
    with open(dst, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["website", "telegram", "emails"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} sites, {sum(1 for r in rows if r['telegram'])} with Telegram")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--js"]
    main(args[0], args[1], "--js" in sys.argv)
