# make_index.py
from pathlib import Path
from datetime import datetime
import re, html

FOLDER = Path(__file__).parent
OUTFILE = FOLDER / "index.html"

def extract_title(p: Path) -> str:
    try:
        # Read a chunk first; fall back to full file if needed
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return p.stem
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if m:
        return html.escape(m.group(1).strip())
    # fallback: first <h1>
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.IGNORECASE | re.DOTALL)
    if m:
        return html.escape(re.sub(r"<.*?>", "", m.group(1)).strip())
    return html.escape(p.stem)

def human_size(n: int) -> str:
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024:
            return f"{n:.0f} {unit}" if unit=="B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"

# Collect .html files (exclude the index we’re writing)
files = sorted(
    [p for p in FOLDER.glob("*.html") if p.name.lower() != "index.html"],
    key=lambda p: p.name.lower()
)

rows = []
for p in files:
    stat = p.stat()
    title = extract_title(p)
    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
    size = human_size(stat.st_size)
    rows.append(f"""\
      <tr>
        <td><a href="{p.name}">{title}</a></td>
        <td class="mono">{p.name}</td>
        <td class="mono">{mtime}</td>
        <td class="mono">{size}</td>
      </tr>""")

html_out = f"""\
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Index of {html.escape(FOLDER.name)}</title>
<style>
  :root {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }}
  body {{ margin: 2rem; }}
  h1 {{ margin: 0 0 1rem; font-size: 1.4rem; }}
  table {{ border-collapse: collapse; width: 100%; max-width: 100ch; }}
  th, td {{ padding: .5rem .6rem; border-bottom: 1px solid #ddd; text-align: left; }}
  th {{ background: #f5f5f5; position: sticky; top: 0; }}
  tr:hover td {{ background: #fafafa; }}
  .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space: nowrap; }}
  footer {{ color: #666; margin-top: 1rem; font-size: .9rem; }}
</style>
<h1>Index of {html.escape(str(FOLDER))}</h1>
<table>
  <thead>
    <tr><th>Title</th><th>File</th><th>Modified</th><th>Size</th></tr>
  </thead>
  <tbody>
    {''.join(rows) if rows else '<tr><td colspan="4">No HTML files found.</td></tr>'}
  </tbody>
</table>
<footer>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer>
</html>
"""

OUTFILE.write_text(html_out, encoding="utf-8")
print(f"Wrote {OUTFILE}")