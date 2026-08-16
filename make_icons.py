"""Generate Home Screen PNG icons if Pillow is installed. Optional."""
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit("Pillow not installed; icons are optional. App still runs.")

root = Path(__file__).resolve().parent / "pwa"
root.mkdir(exist_ok=True)
for size, name in [(180, "apple-touch-icon.png"), (512, "icon-512.png"), (192, "icon-192.png")]:
    im = Image.new("RGB", (size, size), "#0c0d12")
    d = ImageDraw.Draw(im)
    m = int(size * 0.12)
    d.rounded_rectangle([m, m, size - m, size - m], radius=int(size * 0.18), outline="#7c5cff", width=max(3, size // 40))
    d.ellipse([size * 0.22, size * 0.28, size * 0.55, size * 0.72], outline="#e8e6f2", width=max(2, size // 50))
    d.ellipse([size * 0.45, size * 0.28, size * 0.78, size * 0.72], outline="#7c5cff", width=max(2, size // 50))
    im.save(root / name, "PNG")
    print(name)
