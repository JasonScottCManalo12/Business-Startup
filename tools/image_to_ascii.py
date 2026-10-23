#!/usr/bin/env python3
"""Fetch a public HTTPS image and create a vision-friendly preview + ASCII rendering.

Configuration (environment):
  IMAGE_URL: public HTTPS image URL (required)
  PREVIEW_WIDTH: preview width in pixels (default 324, max 1024)
  MAX_DOWNLOAD_BYTES: maximum downloaded bytes (default 25 MiB)
"""
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from PIL import Image, ImageOps, UnidentifiedImageError
import hashlib
import json
import os

OUTPUT = Path("image-ascii.txt")
PREVIEW = Path("image-preview.png")
METADATA = Path("image-metadata.json")
RAMP = "  ..,,::--==++**##%%@@"
MAX_BYTES = int(os.environ.get("MAX_DOWNLOAD_BYTES", str(25 * 1024 * 1024)))

def main():
    url = os.environ.get("IMAGE_URL", "").strip()
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise SystemExit("IMAGE_URL must be a public HTTPS URL without embedded credentials.")
    preview_width = int(os.environ.get("PREVIEW_WIDTH", "324"))
    if not 32 <= preview_width <= 1024:
        raise SystemExit("PREVIEW_WIDTH must be between 32 and 1024 pixels.")

    request = Request(url, headers={"User-Agent": "Business-Startup-Image-Bridge/1.0"})
    with urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise SystemExit(f"Image download failed: HTTP {response.status}")
        content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise SystemExit(f"Image exceeds the {MAX_BYTES}-byte download limit.")
    digest = hashlib.sha256(data).hexdigest()
    source = Path("source-image.bin")
    source.write_bytes(data)

    try:
        with Image.open(source) as original:
            original.load()
            image_format = original.format
            width, height = original.size
            if width < 1 or height < 1 or width * height > 50_000_000:
                raise SystemExit("Image dimensions are invalid or exceed 50 million pixels.")
            preview_height = max(1, round(height * preview_width / width))
            preview = ImageOps.exif_transpose(original).convert("RGB")
            # Recalculate after EXIF orientation is applied.
            width, height = preview.size
            preview_height = max(1, round(height * preview_width / width))
            preview = preview.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            preview.save(PREVIEW, format="PNG", optimize=True)

            ascii_width = 48
            ascii_height = max(1, round(height * ascii_width / width * 0.48))
            gray = ImageOps.grayscale(original).resize(
                (ascii_width, ascii_height), Image.Resampling.LANCZOS
            )
            pixels = list(gray.getdata())
    except (UnidentifiedImageError, OSError) as exc:
        raise SystemExit(f"Downloaded content is not a supported readable image: {exc}")

    levels = len(RAMP) - 1
    lines = []
    for y in range(ascii_height):
        row = pixels[y * ascii_width:(y + 1) * ascii_width]
        lines.append("".join(RAMP[p * levels // 255] for p in row).rstrip())
    OUTPUT.write_text("\\n".join(lines) + "\\n", encoding="utf-8")

    metadata = {
        "source_url": url,
        "http_status": 200,
        "content_type": content_type,
        "format": image_format,
        "width": width,
        "height": height,
        "download_bytes": len(data),
        "sha256": digest,
        "preview_file": PREVIEW.name,
        "preview_width": preview_width,
        "preview_height": preview_height,
        "preview_bytes": PREVIEW.stat().st_size,
        "ascii_file": OUTPUT.name,
        "ascii_width": ascii_width,
        "ascii_height": ascii_height,
    }
    METADATA.write_text(json.dumps(metadata, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    summary = Path(os.environ.get("GITHUB_STEP_SUMMARY", "image-summary.md"))
    summary.write_text(
        "# Image-to-vision bridge result\\n\\n"
        f"- **Source URL:** {url}\\n"
        f"- **Detected format:** {image_format} ({content_type or 'content type not supplied'})\\n"
        f"- **Original dimensions:** {width} × {height}\\n"
        f"- **Downloaded:** {len(data):,} bytes\\n"
        f"- **SHA-256:** `{digest}`\\n"
        f"- **Preview:** {preview_width} × {preview_height} PNG ({PREVIEW.stat().st_size:,} bytes)\\n"
        f"- **ASCII output:** {ascii_width} × {ascii_height} characters\\n\\n"
        "Download the `image-bridge-output` artifact to inspect the PNG, metadata, and ASCII preview.\\n",
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()
