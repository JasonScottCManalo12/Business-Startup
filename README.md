# Business-Startup Tools

This repository contains two browser-only experiments. The root page is a small directory; each application is kept in its own folder to prevent one app from replacing another.

## Applications

- **[JPEG ↔ JSON Bridge](./tools/jpeg-json-bridge/)** — package JPEG bytes as Base64 JSON, reconstruct the image, and validate metadata and SHA-256.
- **[Random Image Generator](./tools/random-image-generator/)** — create abstract JPEGs at 1280×720, 1920×1080, 3840×2160, or 1080×8000 (92% JPEG quality).

## Repository layout

```text
.
├── index.html
├── tools/
│   ├── jpeg-json-bridge/
│   │   └── index.html
│   └── random-image-generator/
│       └── index.html
├── .github/
│   └── workflows/
│       └── jpeg-json-bridge.yml
├── README.md
└── REPORT.md
```

The bridge workflow validates `tools/jpeg-json-bridge/index.html`, rather than assuming the app lives in the root page.

## Documentation

- **[Experiment report](./REPORT.md)** — successful baseline, AI webpage-access observations, evidence, limitations, and open questions.

## JPEG–JSON Bridge at a glance

The bridge packages a JPEG image into a UTF-8 JSON document with metadata and Base64-encoded image bytes. A receiving application can parse the JSON, decode the bytes, validate the result, and render the image.

Example format:

```json
{
  "format": "jpeg-json-bridge",
  "version": 1,
  "filename": "example.jpg",
  "mimeType": "image/jpeg",
  "byteLength": 123456,
  "sha256": "...",
  "encoding": "base64",
  "data": "..."
}
```

Base64 increases payload size compared with the original binary JPEG, so this is a transport/container technique rather than a compression method. The converter is a browser-only proof of concept and reads files selected locally by the user.

**Project status:** Experimental / Proof of Concept. For the test history and current findings, see [REPORT.md](./REPORT.md).
