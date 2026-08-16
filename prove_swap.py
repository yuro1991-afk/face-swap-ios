"""Prove the iOS gateway one-shot swap against the live MultoModa engine."""
from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def data_uri(path: Path) -> str:
    raw = path.read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--gateway", default="http://127.0.0.1:8860")
    p.add_argument("--source", default=str(ROOT / "fixtures" / "portrait-a.jpg"))
    p.add_argument("--target", default=str(ROOT / "fixtures" / "portrait-b.jpg"))
    p.add_argument("--out", default=str(ROOT / "out" / "prove-ios-swap.jpg"))
    args = p.parse_args()

    health = json.loads(urllib.request.urlopen(args.gateway + "/api/ios/health", timeout=8).read())
    if health.get("status") != "ok":
        print("RED health:", json.dumps(health)[:800])
        return 2

    src, tgt = Path(args.source), Path(args.target)
    if not src.is_file() or not tgt.is_file():
        print("RED missing fixtures")
        return 2

    body = json.dumps({"source_image": data_uri(src), "target_image": data_uri(tgt)}).encode()
    req = urllib.request.Request(
        args.gateway + "/api/ios/swap",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        payload = json.loads(resp.read())
    if not payload.get("ok") or not payload.get("image"):
        print("RED swap:", payload)
        return 3

    b64 = payload["image"].split(",", 1)[1]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(b64))
    evidence = {
        "false_green": 0,
        "status": "GREEN",
        "health": health.get("status"),
        "faces": payload.get("faces"),
        "metrics": payload.get("metrics"),
        "engine_path": payload.get("path"),
        "out": str(out),
        "bytes": out.stat().st_size,
    }
    (ROOT / "out" / "PROVE.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
