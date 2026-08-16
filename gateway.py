"""
LAN face for MultoModa Face Studio.
Binds 0.0.0.0 so an iPhone on Wi-Fi can reach the PWA.
Does not import CUDA / InsightFace. Does not start the engine.
"""
from __future__ import annotations

import json
import os
import socket
import sys
import urllib.error
import urllib.request
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PWA = ROOT / "pwa"
ENGINE = os.environ.get("FACESWAP_ENGINE", "http://127.0.0.1:8855").rstrip("/")
PORT = int(os.environ.get("FACESWAP_IOS_PORT", "8860"))
HOST = os.environ.get("FACESWAP_IOS_HOST", "0.0.0.0")


def lan_ipv4() -> list[str]:
    found: list[str] = []
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if ip.startswith("127.") or ip.startswith("169.254."):
                continue
            if ip not in found:
                found.append(ip)
    except OSError:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127.") and ip not in found:
            found.insert(0, ip)
    except OSError:
        pass
    return found


def engine_json(method: str, path: str, body: dict | None = None, timeout: float = 180.0) -> tuple[int, dict]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        ENGINE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            payload = json.loads(raw.decode("utf-8") or "{}")
            return resp.status, payload
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"detail": raw or str(e)}
        return e.code, payload
    except Exception as e:
        return 502, {"detail": f"engine unreachable: {e}"}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PWA), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send_json(self, status: int, payload: dict) -> None:
        blob = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(blob)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(blob)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in ("/api/ios/health", "/api/health"):
            code, engine = engine_json("GET", "/api/health", timeout=5.0)
            ips = lan_ipv4()
            self._send_json(
                200 if code == 200 else 503,
                {
                    "status": "ok" if code == 200 else "degraded",
                    "product": "Face Swap iOS",
                    "gateway": {"host": HOST, "port": PORT, "lan_urls": [f"http://{ip}:{PORT}" for ip in ips]},
                    "engine": {"url": ENGINE, "http": code, "body": engine},
                    "install": "Safari → Share → Add to Home Screen",
                    "false_green": 0,
                },
            )
            return
        if parsed.path.startswith("/api/"):
            code, body = engine_json("GET", parsed.path, timeout=30.0)
            self._send_json(code, body)
            return
        if parsed.path in ("", "/"):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/ios/swap":
            try:
                body = self._read_json()
            except json.JSONDecodeError:
                self._send_json(400, {"ok": False, "error": "invalid JSON"})
                return
            source = body.get("source_image") or body.get("sourceImage")
            target = body.get("target_image") or body.get("targetImage")
            if not source or not target:
                self._send_json(400, {"ok": False, "error": "source_image and target_image are required"})
                return
            face_id = f"ios_{uuid.uuid4().hex[:10]}"
            rcode, registered = engine_json(
                "POST",
                "/api/faces/register",
                {"face_id": face_id, "name": "iphone", "image_base64": source},
            )
            if rcode != 200:
                detail = registered.get("detail") or registered
                self._send_json(rcode, {"ok": False, "error": f"register failed: {detail}"})
                return
            scode, swapped = engine_json(
                "POST",
                "/api/swap",
                {
                    "target_image_base64": target,
                    "source_face_id": face_id,
                    "enhance_blend": True,
                },
            )
            if scode != 200 or not swapped.get("ok"):
                detail = swapped.get("detail") or swapped
                self._send_json(scode, {"ok": False, "error": f"swap failed: {detail}"})
                return
            self._send_json(
                200,
                {
                    "ok": True,
                    "image": swapped.get("image_base64"),
                    "path": swapped.get("path"),
                    "faces": swapped.get("faces"),
                    "metrics": swapped.get("metrics"),
                    "source_face_id": face_id,
                },
            )
            return
        if parsed.path.startswith("/api/"):
            try:
                body = self._read_json()
            except json.JSONDecodeError:
                self._send_json(400, {"detail": "invalid JSON"})
                return
            code, payload = engine_json("POST", parsed.path, body)
            self._send_json(code, payload)
            return
        self._send_json(404, {"detail": "not found"})


def main() -> None:
    if not PWA.is_dir():
        print(f"RED: missing PWA directory {PWA}", file=sys.stderr)
        sys.exit(1)
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    ips = lan_ipv4()
    print(f"Face Swap iOS gateway on http://{HOST}:{PORT}")
    print(f"Engine: {ENGINE}")
    if ips:
        print("Open on iPhone Safari (same Wi-Fi):")
        for ip in ips:
            print(f"  http://{ip}:{PORT}")
        print("Then: Share → Add to Home Screen")
    else:
        print("No LAN IPv4 found. Check Wi-Fi.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
