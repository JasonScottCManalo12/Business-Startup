# JPEG–JSON Bridge

A simple JSON container format for transporting a JPEG image as Base64-encoded data, with metadata for validation and reconstruction.

## Overview

The JPEG–JSON Bridge packages a JPEG image into a UTF-8 JSON document.

Instead of transmitting an image file directly, the image can be represented as a JSON document containing the JPEG bytes encoded as Base64.

The receiving application can then:

1. Fetch the JSON.
2. Parse the JSON.
3. Read the Base64 data.
4. Decode the Base64 data back into JPEG bytes.
5. Verify the reconstructed data.
6. Render the JPEG.

## Format

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

### Fields

| Field | Description |
|---|---|
| `format` | Identifies the JSON container format |
| `version` | Format version |
| `filename` | Original JPEG filename |
| `mimeType` | MIME type of the embedded image |
| `byteLength` | Expected size of the decoded JPEG in bytes |
| `sha256` | SHA-256 hash of the original JPEG bytes |
| `encoding` | Encoding used for the image data |
| `data` | Base64-encoded JPEG data |

## Test File

The first successful end-to-end test used `1000073758.json` from the `feature/jpeg-json-bridge` branch of the Business-Startup repository.

The JSON contained:

- **604,748 characters**
- **453,372 decoded JPEG bytes**
- JPEG dimensions of **720 × 1,604 pixels**
- Base64 encoding
- SHA-256 metadata

The decoded byte count exactly matched the declared `byteLength`.

The embedded JPEG was successfully reconstructed and rendered.

## What the Experiment Demonstrated

The experiment established that the complete conversion pipeline works:

```text
GitHub
   │
   ▼
JSON file
   │
   ▼
Parse JSON
   │
   ▼
Base64 data
   │
   ▼
Decode
   │
   ▼
JPEG bytes
   │
   ▼
Image renderer
   │
   ▼
Original image
```

The Base64-to-JPEG conversion itself was not the problem in this test.

The JSON was fetched successfully, parsed successfully, decoded successfully, and rendered successfully.

## Important Observation

The experiment suggests that when substantially larger payloads fail, the limiting factor may occur during **data retrieval or transfer**, rather than during JPEG reconstruction.

Possible limiting factors include:

- response-size limits
- request-size limits
- text/character limits
- token/context limits when data passes through an AI system
- transport truncation
- processing or memory limits
- timeout limits

However, the exact failure boundary has **not yet been established**.

The successful 604 KB test should therefore be treated as a **known working point**, not as the maximum supported size.

## Future Testing

The next experiment is to increase payload size while keeping the JPEG–JSON format and decoding process unchanged.

Suggested test sequence:

```text
~600 KB   Known successful baseline
~1 MB     First larger test
~5 MB     Large payload test
~10 MB    Substantial payload test
~20 MB+   Extended limit testing
```

For each test, record:

- JSON character count
- JSON byte size
- Base64 character count
- decoded JPEG byte size
- whether the complete JSON was fetched
- whether JSON parsing succeeded
- whether Base64 decoding succeeded
- whether the decoded byte count matches `byteLength`
- whether the JPEG renders
- whether the SHA-256 hash matches

This allows the failure point to be isolated instead of assuming that the image conversion is responsible.

## Validation Model

A receiving application should ideally validate:

```text
1. JSON syntax
2. format
3. version
4. mimeType
5. encoding
6. Base64 decoding
7. decoded byteLength
8. JPEG signature
9. SHA-256
10. image dimensions
```

For example:

```text
JSON valid?
     │
     ├── No → Reject
     │
     ▼
Base64 valid?
     │
     ├── No → Reject
     │
     ▼
Decoded length == byteLength?
     │
     ├── No → Reject
     │
     ▼
SHA-256 matches?
     │
     ├── No → Reject
     │
     ▼
Valid JPEG
     │
     ▼
Render
```

## Why Use JSON?

The bridge is useful when an application already operates around JSON-based data transport and needs to carry an image together with metadata.

Advantages include:

- Single structured payload
- Explicit metadata
- Easy parsing in web applications
- Easy validation
- Self-describing format
- Image and metadata can travel together
- No dependency on a separate image URL during transport

The trade-off is that Base64 increases the size of binary data compared with the original JPEG.

Therefore, this format is primarily a **transport/container technique**, not a compression technique.

## Project Status

**Status:** Experimental / Proof of Concept

**Version:** 1

**Current result:** End-to-end JPEG-in-JSON retrieval, decoding, validation, and rendering successfully demonstrated.

**Known successful payload:** `1000073758.json` — approximately 605 KB JSON containing a 453 KB JPEG.

**Next objective:** Determine the practical maximum payload size and identify whether failures occur during retrieval, parsing, decoding, validation, or rendering.

## Experiment Log

### October 23, 2026

Initial end-to-end test completed successfully.

The experiment began after investigating whether a long JSON payload containing an embedded JPEG could be fetched and reconstructed.

The test demonstrated that the JPEG–JSON conversion pipeline itself can successfully handle the tested payload.

The remaining question is the upper limit of the retrieval/transport path.

> **Current lesson:** Don't assume the converter is broken just because the data didn't arrive. Isolate the pipeline and measure each stage.
