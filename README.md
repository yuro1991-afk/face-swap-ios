# Face Swap iOS

iPhone Home Screen app for the **local** MultoModa Face Studio engine already running on the host.

Clone → start the LAN gateway → Safari on the iPhone → **Add to Home Screen**.

This is **not** an App Store IPA. Apple does not allow “git clone, tap, install on any iPhone” for unsigned native apps. See [HONESTY.md](HONESTY.md).

## Requirements

- Windows host with MultoModa Face Studio healthy at `http://127.0.0.1:8855/api/health`
- iPhone on the **same Wi-Fi**
- Python 3.10+ on the host (stdlib only for the gateway)

## Install on an iPhone

1. On the host:

```bat
git clone https://github.com/yuro1991-afk/face-swap-ios.git
cd face-swap-ios
START.cmd
```

2. Read the printed URL, for example `http://192.168.1.102:8860`
3. On the iPhone, open that URL in **Safari** (not Chrome).
4. Tap Share → **Add to Home Screen** → Add.
5. Open the new **Face Swap** icon.
6. Pick **Your face** and **Target photo** → **Swap face**.
7. Hold the result → **Save to Photos**, or use **Save**.

If the page does not load, allow Windows Firewall for TCP **8860**, and confirm the phone is on the same LAN (not cellular).

## What runs where

| Piece | Where | GPU |
|-------|--------|-----|
| PWA UI | iPhone Safari / Home Screen | No |
| `gateway.py` `:8860` | This PC, all interfaces | No |
| MultoModa `:8855` | This PC, localhost | Existing daemon only |

## API the phone uses

- `GET /api/ios/health` — engine + LAN URLs
- `POST /api/ios/swap` `{ "source_image": "data:image/jpeg;base64,...", "target_image": "..." }`

## Swift (optional, Mac only)

`ios/FaceSwap` is a WKWebView shell. Open it in Xcode on a Mac, set the LAN URL, sign with your Apple ID. That is **not** produced on this Windows host.

## License

Apache-2.0 for original files in this repo. InsightFace weights stay on the host and are **not** in git.
