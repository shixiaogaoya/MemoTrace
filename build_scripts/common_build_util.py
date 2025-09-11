import os
from pathlib import Path
from memotrace_version import __version__, __app_name__, __description__

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None


def ensure_icon(root: Path) -> Path:
    icon_dir = root / "assets"
    icon_dir.mkdir(exist_ok=True)
    icon_file = icon_dir / "icon.ico"
    if icon_file.exists():
        return icon_file
    if Image is None:
        # 写入一个最小ICO占位（二进制16x16单色）
        icon_file.write_bytes(b"\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x04\x00(\x01\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00\x04\x00\x00\x00\x00\x00\x00\x01\x00\x00\x13\x0B\x00\x00\x13\x0B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x00\x00\xFF\xFF\xFF\x00\x00\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\xF0\x00\x00\x00\x00\x00\x00\x00")
        return icon_file
    # 生成简单图标
    img = Image.new("RGBA", (256, 256), (30, 30, 30, 255))
    d = ImageDraw.Draw(img)
    text = "M"
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    d.text((110, 110), text, fill=(0, 200, 255, 255), font=font)
    img.save(icon_file, sizes=[(256,256),(128,128),(64,64),(32,32),(16,16)])
    return icon_file


def create_version_file(root: Path) -> Path:
    vf = root / "build_scripts" / "version_info.txt"
    content = f"""# Auto-generated version info
# {__app_name__} {__version__}
# {__description__}
"""
    vf.write_text(content, encoding="utf-8")
    return vf

__all__ = ["ensure_icon", "create_version_file", "__version__", "__app_name__", "__description__"]
