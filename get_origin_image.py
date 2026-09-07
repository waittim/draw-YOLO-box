#!/usr/bin/env python3
# coding: utf-8
"""Copy original images that correspond to wrongly annotated samples."""

from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path
from typing import List, Optional, Sequence

import cv2

try:
    import piexif
except ImportError:  # optional dependency
    piexif = None

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

DEFAULT_RAW_IMAGE_FOLDER = "./raw_images/"
DEFAULT_OUTPUT_IMAGE_FOLDER = "./save_image/"
DEFAULT_IMAGE_NAME_LIST_PATH = "./name_list.txt"
DEFAULT_WRONG_IMAGE_FOLDER = "./wrong/"

logger = logging.getLogger(__name__)


def find_image_path(folder: str, stem: str) -> Optional[Path]:
    base = Path(folder)
    for ext in sorted(IMAGE_EXTENSIONS):
        candidate = base / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    if base.is_dir():
        for path in base.iterdir():
            if path.is_file() and path.stem == stem and path.suffix.lower() in IMAGE_EXTENSIONS:
                return path
    return None


def make_name_list(wrong_image_folder: str, image_name_list_path: str) -> List[str]:
    folder = Path(wrong_image_folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"wrong-image folder not found: {wrong_image_folder}")

    stems: List[str] = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        stems.append(path.stem)

    list_path = Path(image_name_list_path)
    with list_path.open("w", encoding="utf-8") as handle:
        for stem in stems:
            handle.write(stem + "\n")
    return stems


def read_name_list(image_name_list_path: str) -> List[str]:
    """Read one stem per line so filenames with spaces survive."""
    path = Path(image_name_list_path)
    if not path.is_file():
        raise FileNotFoundError(f"name list not found: {image_name_list_path}")
    with path.open("r", encoding="utf-8") as handle:
        # Important: split on newlines, not whitespace (PR #4 / issue space-names).
        return [line.strip() for line in handle.read().split("\n") if line.strip()]


def get_image(
    image_stem: str,
    raw_image_folder: str,
    output_image_folder: str,
    strip_exif: bool = True,
) -> bool:
    if image_stem.startswith("."):
        return False

    image_path = find_image_path(raw_image_folder, image_stem)
    if image_path is None:
        logger.warning("original image not found for stem %r", image_stem)
        return False

    out_dir = Path(output_image_folder)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{image_stem}{image_path.suffix.lower()}"

    # Prefer binary copy to preserve bytes; fall back to cv2 if needed.
    try:
        shutil.copy2(image_path, out_path)
    except OSError:
        image = cv2.imread(str(image_path))
        if image is None:
            logger.warning("failed to read %s", image_path)
            return False
        if not cv2.imwrite(str(out_path), image):
            logger.error("failed to write %s", out_path)
            return False

    if strip_exif and piexif is not None and out_path.suffix.lower() in {".jpg", ".jpeg"}:
        try:
            piexif.remove(str(out_path))
        except Exception as exc:  # noqa: BLE001 — best-effort EXIF strip
            logger.debug("piexif.remove skipped for %s: %s", out_path, exc)
    elif strip_exif and piexif is None:
        logger.debug("piexif not installed; skipping EXIF strip")

    return True


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy original images corresponding to wrongly annotated samples."
    )
    parser.add_argument("--wrong", default=DEFAULT_WRONG_IMAGE_FOLDER, help="Folder of wrong boxed images")
    parser.add_argument("--images", default=DEFAULT_RAW_IMAGE_FOLDER, help="Raw original image folder")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_IMAGE_FOLDER, help="Output folder")
    parser.add_argument("--name-list", default=DEFAULT_IMAGE_NAME_LIST_PATH, help="Stem list path")
    parser.add_argument("--keep-exif", action="store_true", help="Do not strip JPEG EXIF")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    make_name_list(args.wrong, args.name_list)
    stems = read_name_list(args.name_list)

    ok = 0
    for stem in stems:
        logger.info("processing %s", stem)
        if get_image(stem, args.images, args.output, strip_exif=not args.keep_exif):
            ok += 1
    logger.info("done: copied %d / %d", ok, len(stems))
    return 0 if ok == len(stems) else 1


if __name__ == "__main__":
    raise SystemExit(main())
