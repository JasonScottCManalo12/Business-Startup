# JPEG–JSON Bridge: Experiment Report

**Repository:** [Business-Startup](https://github.com/JasonScottCManalo12/Business-Startup)  
**Status:** Experimental / Proof of Concept  
**Report date:** October 24, 2026

## 1. Purpose

This experiment investigates whether a JPEG can be packaged inside a JSON document as Base64 data, retrieved, reconstructed, validated, and rendered. It also explores why different AI systems can have different results when asked to inspect the same webpage or image resource.

## 2. Project components

- **JPEG ↔ JSON Bridge:** [tools/jpeg-json-bridge/](./tools/jpeg-json-bridge/) — browser-only conversion and reconstruction tool.
- **Random Image Generator:** [tools/random-image-generator/](./tools/random-image-generator/) — creates abstract JPEG test images at 1280×720, 1920×1080, 3840×2160, and 1080×8000.
- **Published site:** https://jasonscottcmanalo12.github.io/Business-Startup/

The bridge reads a JPEG selected locally by the user. It encodes the bytes as Base64 in a JSON document and can reconstruct the image, checking metadata such as byte length, JPEG signature, and SHA-256. The browser-only converter does not itself fetch remote images; it uses local file selection and browser Blob URLs.

## 3. Known successful baseline

An earlier end-to-end test used `1000073758.json` from the `feature/jpeg-json-bridge` branch.

Reported test results:

- JSON length: **604,748 characters**
- Decoded JPEG size: **453,372 bytes**
- JPEG dimensions: **720 × 1,604 pixels**
- Encoding: Base64
- The decoded byte count matched the declared `byteLength`.
- The embedded JPEG was reconstructed and rendered successfully.

This establishes a known working test case, not a maximum supported payload size.

## 4. Large-image and AI-access observations

The test image under investigation is `random-image-1080x8000.jpg` (1080 × 8000 pixels). The user tested the published webpage with several AI systems and reported these results:

| AI system | Reported observation |
|---|---|
| Gemini | Successfully described the webpage. |
| Manus AI | Successfully described the whole webpage. |
| Grok | Successfully described the whole webpage. |
| Claude | Reported that system policy blocks access to the image. |
| Perplexity | Could not access the link itself. |
| Meta AI | Could not open or see the image. |

Separately, attempts to process the tall image through an AI-facing JSON workflow failed, while a smaller JSON-embedded JPEG had worked. The exact failure stage for the tall-image workflow has not been conclusively identified.

These observations describe the tested systems' reported behavior. They do **not** prove that every system used the same retrieval method, that the successful systems decoded the JSON directly, or that the failed systems' visual models are incapable of interpreting the image.

## 5. What the evidence supports

1. The JPEG–JSON pipeline has worked end to end for the documented 453,372-byte JPEG.
2. At least three tested AI systems reportedly inspected the published webpage successfully.
3. Other tested systems reported access failures or restrictions.
4. Different AI systems may use different browsing, URL retrieval, security, rendering, and image-processing paths.
5. The browser converter's local-file workflow does not itself establish or diagnose server-side CORS behavior.

## 6. What remains unproven

The available observations do not yet identify the precise failure boundary for the 1080 × 8000 image. Possible stages include:

- URL or resource access;
- response retrieval or truncation;
- JSON parsing;
- Base64 decoding;
- image-dimension or format handling;
- visual rendering or AI image interpretation;
- system-specific access policy.

These are hypotheses, not confirmed causes. A successful description of a webpage alone does not establish that an AI fetched and decoded the original JPEG or its JSON representation directly.

## 7. Conclusion

The current evidence does not justify concluding that the converter or source image is defective. It shows that a smaller JPEG-in-JSON payload can be reconstructed successfully and that AI systems differ in their ability or permission to access the tested webpage and image resources.

The next investigation should build on the evidence already collected and isolate the specific failing stage, rather than repeat completed tests or change working code without a demonstrated cause.

> **Working principle:** When a resource fails in one AI system, distinguish access, retrieval, decoding, rendering, and interpretation before assigning blame to the file or converter.
