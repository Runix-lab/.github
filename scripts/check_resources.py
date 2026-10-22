"""Validate public Markdown links and the published synthetic exercise offline."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_URL = "https://github.com/Runix-lab/.github/blob/main/"
pages = [ROOT / "CONTRIBUTING.md", *sorted((ROOT / "profile").glob("*.md")),
         *sorted((ROOT / "learning").glob("*.md"))]
for page in pages:
    text = page.read_text()
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if link.startswith(LOCAL_URL):
            target = ROOT / link.removeprefix(LOCAL_URL)
        elif ":" in link or link.startswith("#"):
            continue
        else:
            target = page.parent / link.split("#", 1)[0]
        if not target.exists():
            raise SystemExit(f"Missing link target: {page.relative_to(ROOT)}: {link}")

guide = (ROOT / "learning/embodied-ai.md").read_text()
blocks = re.findall(r"```python\n(.*?)\n```", guide, re.S)
expected = re.search(r"Expected output:\n\n```text\n(.*?)\n```", guide, re.S)
if len(blocks) != 1 or expected is None:
    raise SystemExit("The embodied exercise needs one runnable block and expected output")
result = subprocess.run([sys.executable, "-c", blocks[0]], text=True,
                        capture_output=True, timeout=10, check=True)
if result.stdout != expected.group(1) + "\n":
    raise SystemExit(f"Exercise output changed: {result.stdout!r}")
print(f"PASS: local links in {len(pages)} public documents and exact exercise output")
