"""Create a clean-white A4 PDF from a photographed paper document."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


OUT_SIZE = (2480, 3508)


def parse_corners(value: str, width: int, height: int) -> tuple[float, ...]:
    points = []
    for item in value.split(";"):
        pair = item.split(",")
        if len(pair) != 2:
            raise ValueError("corners must be TLx,TLy;TRx,TRy;BRx,BRy;BLx,BLy")
        point = (float(pair[0]), float(pair[1]))
        if not (0 <= point[0] < width and 0 <= point[1] < height):
            raise ValueError(f"corner outside image: {point}")
        points.append(point)
    if len(points) != 4:
        raise ValueError("exactly four corners are required")
    tl, tr, br, bl = points
    # Pillow QUAD order is TL, BL, BR, TR.
    return (*tl, *bl, *br, *tr)


def flatten_gray(page: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(page)
    small = gray.resize((310, 439), Image.Resampling.BILINEAR)
    background = small.filter(ImageFilter.GaussianBlur(20)).resize(
        gray.size, Image.Resampling.BICUBIC
    )
    src = np.asarray(gray, dtype=np.float32)
    bg = np.asarray(background, dtype=np.float32)
    flat = np.clip(src * (247.0 / np.maximum(bg, 30.0)), 0, 255)
    flat = np.where(flat >= 232, 255, flat)
    flat = np.where(
        (flat >= 185) & (flat < 232), 205 + (flat - 185) * (50 / 47), flat
    )
    flat = np.where(flat < 185, (flat - 128) * 1.16 + 128, flat)
    result = Image.fromarray(np.clip(flat, 0, 255).astype(np.uint8), "L")
    result = ImageEnhance.Contrast(result).enhance(1.08)
    return result.filter(ImageFilter.UnsharpMask(1.0, 125, 3)).convert("RGB")


def flatten_color(page: Image.Image) -> Image.Image:
    small = page.resize((310, 439), Image.Resampling.BILINEAR)
    background = small.filter(ImageFilter.GaussianBlur(18)).resize(
        page.size, Image.Resampling.BICUBIC
    )
    src = np.asarray(page, dtype=np.float32)
    bg = np.asarray(background, dtype=np.float32)
    flat = src * (246.0 / np.maximum(bg, 25.0))
    flat = np.clip((flat - 128.0) * 1.18 + 135.0, 0, 255).astype(np.uint8)
    result = ImageOps.autocontrast(Image.fromarray(flat, "RGB"), cutoff=(0.15, 0.45))
    result = result.filter(ImageFilter.UnsharpMask(1.1, 135, 2))
    arr = np.asarray(result).copy()
    spread = arr.max(axis=2) - arr.min(axis=2)
    luminance = arr.mean(axis=2)
    arr[(luminance > 222) & (spread < 13)] = 255
    return Image.fromarray(arr, "RGB")


def choose_mode(page: Image.Image) -> str:
    sample = np.asarray(page.resize((400, 565), Image.Resampling.BILINEAR))
    chroma = sample.max(axis=2) - sample.min(axis=2)
    dark_or_colored = sample.mean(axis=2) < 235
    ratio = np.mean((chroma > 34) & dark_or_colored)
    return "color" if ratio > 0.001 else "grayscale"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--corners", help="TLx,TLy;TRx,TRy;BRx,BRy;BLx,BLy")
    parser.add_argument("--mode", choices=("auto", "color", "grayscale"), default="auto")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(args.input) as raw:
        source = ImageOps.exif_transpose(raw).convert("RGB")
    width, height = source.size
    quad = (
        parse_corners(args.corners, width, height)
        if args.corners
        else (0, 0, 0, height - 1, width - 1, height - 1, width - 1, 0)
    )
    page = source.transform(
        OUT_SIZE, Image.Transform.QUAD, quad, resample=Image.Resampling.BICUBIC
    )
    mode = choose_mode(page) if args.mode == "auto" else args.mode
    clean = flatten_color(page) if mode == "color" else flatten_gray(page)

    with tempfile.TemporaryDirectory() as temp_dir:
        scan = Path(temp_dir) / "scan.jpg"
        clean.save(scan, "JPEG", quality=96, dpi=(300, 300), subsampling=0)
        page_width, page_height = A4
        pdf = canvas.Canvas(str(args.output), pagesize=A4, pageCompression=1)
        pdf.setTitle(f"{args.input.stem} - 高清净白扫描版")
        pdf.drawImage(str(scan), 0, 0, page_width, page_height)
        pdf.showPage()
        pdf.save()

    print(f"mode={mode}")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
