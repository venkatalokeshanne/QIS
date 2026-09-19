"""Extract webpack modules (by id) from the pretty-printed TrendSpider worker bundle."""
import re, sys
from pathlib import Path
B = Path(r"C:\Users\annev\Downloads\trendspider-automation\data\extraction\runtime_bundle\00_pretty.js")
lines = B.read_text(encoding="utf-8").split("\n")
starts = {}
for i, l in enumerate(lines):
    m = re.match(r"^      (\d+)\((e|e, t|e, t, n)\) \{", l)
    if m:
        starts[m.group(1)] = i
order = sorted(starts.values())
def module(mid):
    s = starts[mid]
    nxt = next((o for o in order if o > s), len(lines))
    return "\n".join(lines[s:nxt])
out = [module(m) for m in sys.argv[2:]]
Path(sys.argv[1]).write_text("\n".join(out), encoding="utf-8")
print(sum(len(o.split(chr(10))) for o in out), "lines")
