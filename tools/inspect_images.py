#!/usr/bin/env python3
"""Inspect repository-hosted JPEGs without uploading them to ChatGPT."""
import hashlib
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from PIL import Image, UnidentifiedImageError

FILES = {
    "random-image-3840x2160.jpg": (3840, 2160),
    "random-image-1920x1080.jpg": (1920, 1080),
    "random-image-1280x720.jpg": (1280, 720),
    "random-image-1080x8000.jpg": (1080, 8000),
}
BASE_URL = "https://raw.githubusercontent.com/JasonScottCManalo12/Business-Startup/main/"
TIMEOUT_SECONDS = 60

def inspect_file(filename, expected_size):
    result = {
        "filename": filename, "url": BASE_URL + filename,
        "expected_dimensions": list(expected_size), "http_status": None,
        "content_type": None, "bytes": None, "sha256": None, "format": None,
        "actual_dimensions": None, "decode_ok": False,
        "dimension_match": False, "error": None,
    }
    try:
        request = urllib.request.Request(
            result["url"], headers={"User-Agent": "Business-Startup-JPEG-Inspector/1.0"}
        )
        digest, total = hashlib.sha256(), 0
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            result["http_status"] = response.status
            result["content_type"] = response.headers.get("Content-Type")
            with tempfile.NamedTemporaryFile(suffix=".jpg") as temp:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    temp.write(chunk)
                    digest.update(chunk)
                    total += len(chunk)
                temp.flush()
                result["bytes"] = total
                result["sha256"] = digest.hexdigest()
                with Image.open(temp.name) as image:
                    result["format"] = image.format
                    result["actual_dimensions"] = list(image.size)
                    image.verify()
                with Image.open(temp.name) as image:
                    image.load()
                result["decode_ok"] = result["format"] == "JPEG"
                result["dimension_match"] = result["actual_dimensions"] == list(expected_size)
                if result["format"] != "JPEG":
                    result["error"] = "Downloaded content is not recognized as JPEG."
                elif not result["dimension_match"]:
                    result["error"] = "Actual dimensions do not match filename."
                elif not result["decode_ok"]:
                    result["error"] = "JPEG decode check failed."
    except urllib.error.HTTPError as exc:
        result["http_status"] = exc.code
        result["error"] = f"HTTP error: {exc}"
    except (urllib.error.URLError, TimeoutError, OSError, UnidentifiedImageError, ValueError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    except Exception as exc:
        result["error"] = f"Unexpected {type(exc).__name__}: {exc}"
    result["passed"] = (
        result["http_status"] == 200 and result["format"] == "JPEG"
        and result["decode_ok"] and result["dimension_match"]
        and result["sha256"] is not None
    )
    return result

def main():
    results = [inspect_file(name, dims) for name, dims in FILES.items()]
    output = {"repository": "JasonScottCManalo12/Business-Startup", "results": results}
    Path("jpeg-inspection-results.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        lines = [
            "# JPEG inspection results", "",
            "Each file was downloaded from its raw repository URL. The script records HTTP metadata, byte size, SHA-256, actual dimensions, and whether Pillow can verify and fully decode the JPEG.", "",
            "| File | HTTP | Bytes | Expected | Actual | SHA-256 | Decode | Result |",
            "|---|---:|---:|---|---|---|---|---|",
        ]
        for r in results:
            expected = " × ".join(map(str, r["expected_dimensions"]))
            actual = " × ".join(map(str, r["actual_dimensions"])) if r["actual_dimensions"] else "—"
            sha = r["sha256"][:16] + "…" if r["sha256"] else "—"
            lines.append(f"| {r['filename']} | {r['http_status'] or '—'} | {r['bytes'] or '—'} | {expected} | {actual} | {sha} | {'PASS' if r['decode_ok'] else 'FAIL'} | {'PASS' if r['passed'] else 'FAIL'} |")
            if r["error"]:
                lines.extend(["", f"**{r['filename']} error:** {r['error']}"])
        lines.extend([
            "", "## Interpretation", "",
            "- HTTP 200 means the raw endpoint served a response; it does not by itself prove the JPEG is valid.",
            "- Decode PASS means the file passed structural verification and full pixel decoding.",
            "- SHA-256 helps identify identical downloaded bytes across runs or sources.",
            "- This tests GitHub delivery and JPEG integrity, not ChatGPT's internal image-processing behavior.",
        ])
        Path(summary_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if all(r["passed"] for r in results) else 1

if __name__ == "__main__":
    sys.exit(main())
