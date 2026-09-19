"""Strip the store-page HTML wrapper from scraped TrendSpider scripts.

The scraper saved each script as `<code x-ref="code" class="hljs"
data-clipboard-text>...</code>`; everything between is the verbatim
script (no HTML-escaping was found in any of the 291 files).
"""
import html
import json
import re
from pathlib import Path

SRC = Path(r"C:\Users\annev\Downloads\trendspider-automation\data\store_indicators")
OUT = Path(__file__).parent / "clean"
OUT.mkdir(exist_ok=True)

manifest = json.loads((SRC / "manifest.json").read_text(encoding="utf-8"))
index = {}
for key, meta in manifest.items():
    if not meta.get("has_source"):
        continue
    raw = (SRC / "sources" / Path(meta["file"]).name).read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"^\s*<code[^>]*>", "", raw)
    body = re.sub(r"</code>\s*$", "", body)
    if "&lt;" in body or "&amp;" in body or "&gt;" in body:
        body = html.unescape(body)
    name = Path(meta["file"]).stem
    (OUT / f"{name}.js").write_text(body, encoding="utf-8")
    index[name] = {"title": meta["title"], "developer": meta["developer"], "url": meta["url"]}
(Path(__file__).parent / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
print(f"cleaned {len(index)} scripts -> {OUT}")
