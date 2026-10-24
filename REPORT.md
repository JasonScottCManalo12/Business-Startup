# JPEG–JSON Bridge: Experiment Report

**Repository:** [Business-Startup](https://github.com/JasonScottCManalo12/Business-Startup)  
**Status:** Experimental / Proof of Concept  
**Report date:** October 24, 2026  
**Latest experiment note:** October 24, 2026, 10:03 PHT (UTC+08:00)

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
| ChatGPT, temporary chat | Successfully described the webpage and its contents, according to the user. |
| ChatGPT, new chat | The user subsequently confirmed that the same website test worked in a new chat. |
| ChatGPT, original conversation | The current conversation's web-retrieval path failed to retrieve the live page/image; GitHub source inspection was possible through a separate route earlier, but a later GitHub tool attempt required approval/login and was stopped. |

Separately, attempts to process the tall image through an AI-facing JSON workflow failed, while a smaller JSON-embedded JPEG had worked. The exact failure stage for the tall-image workflow has not been conclusively identified.

### 4.1 Timestamped cross-chat observation

**Recorded:** October 24, 2026, 10:03 PHT (UTC+08:00).

In the original conversation, attempts to retrieve the published page and the original 1080 × 8000 JPEG failed with a `Cache miss`. An attempt to use the connected GitHub route then encountered an approval/login requirement; the route was not retried after that response.

The user reported that a temporary ChatGPT chat successfully described the webpage, then reported that the test also worked in a new chat. This is evidence of different outcomes across conversations for the same public resource, based on the user's observed tests.

**What this supports:** the access or retrieval experience can differ between conversations or attempts. The failure in the original conversation is not, by itself, evidence that the public page or JPEG is defective.

**What this does not establish:** we do not have a tool-call trace from the successful temporary/new chats. We therefore cannot conclude whether those chats used browser rendering, direct image retrieval, a different fetch path, cache, another tool, or a retry. The suggestion that the successful chat avoided `fetch` remains a hypothesis, not a verified finding.

## 5. What the evidence supports

1. The JPEG–JSON pipeline has worked end to end for the documented 453,372-byte JPEG.
2. At least three tested AI systems reportedly inspected the published webpage successfully.
3. The user also reported successful webpage descriptions in ChatGPT temporary and new chats, while the original conversation's retrieval path failed.
4. Different AI systems, sessions, or attempts may use different browsing, URL retrieval, security, rendering, and image-processing paths.
5. The browser converter's local-file workflow does not itself establish or diagnose server-side CORS behavior.
6. A successful webpage description does not, by itself, prove that the system directly decoded the JSON representation or fetched the original image through a particular mechanism.

## 6. What remains unproven

The available observations do not yet identify the precise failure boundary for the 1080 × 8000 image or explain the cross-chat differences. Possible stages include:

- URL or resource access;
- response retrieval, caching, or truncation;
- JSON parsing;
- Base64 decoding;
- image-dimension or format handling;
- browser rendering or AI image interpretation;
- session-specific tool availability or access policy;
- transient retrieval failure or retry behavior.

These are hypotheses, not confirmed causes. We cannot infer the successful chats' internal tool path from their descriptions alone.

## 7. Conclusion

The current evidence does not justify concluding that the converter or source image is defective. It shows that a smaller JPEG-in-JSON payload can be reconstructed successfully, that AI systems differ in their reported access to the tested webpage, and that the same user-reported webpage test succeeded in new/temporary ChatGPT chats while retrieval failed in the original conversation.

The next investigation should build on the evidence already collected and isolate the specific failing stage, rather than repeat completed tests or change working code without a demonstrated cause. For cross-chat comparisons, record the observed result and exact time, but label internal retrieval explanations as unverified unless tool traces or other direct evidence are available.

> **Working principle:** When a resource fails in one AI system or conversation, distinguish access, retrieval, decoding, rendering, and interpretation before assigning blame to the file or converter.
