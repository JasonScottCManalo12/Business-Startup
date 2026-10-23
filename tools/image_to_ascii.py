#!/usr/bin/env python3
"""Download a public GitHub JPEG and produce a compact ASCII preview."""
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps
import hashlib
import os

URL = "https://raw.githubusercontent.com/JasonScottCManalo12/Business-Startup/main/random-image-1080x8000.jpg"
OUTPUT = Path("image-ascii.txt")
WIDTH = 48
RAMP = "  ..,,::--==++**##%%@@"

def main():
    request = Request(URL, headers={"User-Agent": "Business-Startup-ASCII-Bridge/1.0"})
    with urlopen(request, timeout=60) as response:
        data = response.read()
        print(f"HTTP: {response.status}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
    digest = hashlib.sha256(data).hexdigest()
    source = Path("source-image.jpg")
    source.write_bytes(data)
    with Image.open(source) as original:
        original.load()
        print(f"Format: {original.format}")
        print(f"Dimensions: {original.width}x{original.height}")
        print(f"Bytes: {len(data)}")
        print(f"SHA-256: {digest}")
        height = max(1, round(original.height * WIDTH / original.width * 0.48))
        gray = ImageOps.grayscale(original).resize((WIDTH, height), Image.Resampling.LANCZOS)
        pixels = list(gray.getdata())
    levels = len(RAMP) - 1
    lines = []
    for y in range(height):
        row = pixels[y * WIDTH:(y + 1) * WIDTH]
        lines.append("".join(RAMP[p * levels // 255] for p in row).rstrip())
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ASCII preview: {WIDTH} columns x {height} rows")
    print("----- ASCII PREVIEW START -----")
    print(OUTPUT.read_text(encoding="utf-8"))
    print("----- ASCII PREVIEW END -----")
    summary = Path(os.environ["GITHUB_STEP_SUMMARY"])
    summary.write_text(
        "# JPEG-to-ASCII interpreter test\n\n"
        f"- Source: [original JPEG]({URL})\n"
        "- Dimensions: 1080 × 8000\n"
        f"- Downloaded bytes: {len(data)}\n"
        f"- SHA-256: {digest}\n"
        f"- ASCII preview: {WIDTH} columns × {height} rows\n\n"
        "The full preview is printed in the workflow log and saved as an artifact. "
        "ASCII is a lossy brightness representation, not full vision understanding.\n",
        encoding="utf-8"
    )

if __name__ == "__main__":
    main()
