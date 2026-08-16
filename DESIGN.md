# Face Swap iOS — design

**Product:** iPhone-installable client for the already-working local face-swap engine.  
**Engine:** MultoModa Face Studio · `http://127.0.0.1:8855` · InsightFace `buffalo_l` + `inswapper_128.onnx`  
**false_green:** 0

## Located working apps (disk, this host)

| App | Path | Live now | Role |
|-----|------|----------|------|
| MultoModa Face Studio | `G:\\AI-Home\\projects\\multomoda-face-studio` | YES `:8855` localhost, engines ready | **Canonical local swap** |
| Face Swap AI (local worker) | `C:\\Users\\yuro1\\Downloads\\face-swap-ai` | worker on disk; not the process on `:3000` | Proven iPhone AVIF path |
| Remix MVLLM | `OneDrive\\Desktop\\MultoModa\\MODELS\\remix-mvllm-live-face-swap-&-cv-studio` | YES `:3000` `provider: spacexai` | Cloud, not used |

## Honesty — “install on any iPhone from git”

Apple does **not** let a git clone become a signed `.ipa` that any iPhone will install.

This repo ships the path that actually works: a standalone iOS Home Screen web app served on the LAN, talking to the live local engine. A SwiftUI WKWebView shell is included for a future Mac build. It is **not** a compiled IPA.

## Requirements

1. Clone from GitHub; run one start command on the host that already runs MultoModa.
2. iPhone on the same Wi-Fi opens the printed URL in Safari.
3. Share → Add to Home Screen → icon launches full-screen.
4. Pick source face + target photo (Photos or Camera).
5. HEIC/AVIF converted to JPEG on the phone before upload.
6. Downscale long edge to 1280.
7. One-shot swap via MultoModa.
8. Show result; user can save to Photos.
9. Do not start a second GPU trainer. Use the existing `:8855` daemon.
10. No API keys in the client. Local InsightFace only.

## Architecture

```
iPhone Safari / Home Screen
        HTTP LAN :8860
Windows gateway.py  (0.0.0.0, no GPU)
        HTTP 127.0.0.1:8855
MultoModa Face Studio (already running)
```

## Non-goals

- App Store listing
- On-device InsightFace
- Changing the live MultoModa bind from localhost
- Stealing the 3060 from a train
- Cloud face swap
