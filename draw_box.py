#!/usr/bin/env python3
# coding: utf-8
"""Draw YOLO-format bounding boxes onto images for annotation QA."""

from __future__ import annotations

import argparse
import logging
import os
import random
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import cv2

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

DEFAULT_LABEL_FOLDER = "./labels/"
DEFAULT_RAW_IMAGE_FOLDER = "./raw_images/"
DEFAULT_OUTPUT_IMAGE_FOLDER = "./save_image/"
DEFAULT_IMAGE_NAME_LIST_PATH = "./name_list.txt"
DEFAULT_CLASS_PATH = "./classes.txt"

logger = logging.getLogger(__name__)


def plot_one_box(
    xyxy: Sequence[float],
    image,
    color: Optional[Sequence[int]] = None,
    label: Optional[str] = None,
    line_thickness: Optional[int] = None,
) -> None:
    """Draw one bounding box (and optional label) on an image."""
    tl = line_thickness or round(0.002 * (image.shape[0] + image.shape[1]) / 2) + 1
    color = list(color) if color is not None else [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))
    cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if not label:
        return
    tf = max(tl - 1, 1)
    t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
    c2_bg = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(image, c1, c2_bg, color, -1, cv2.LINE_AA)
    cv2.putText(
        image,
        label,
        (c1[0], c1[1] - 2),
        0,
        tl / 3,
        [225, 255, 255],
        thickness=tf,
        lineType=cv2.LINE_AA,
    )


def find_image_path(raw_image_folder: str, stem: str) -> Optional[Path]:
    """Resolve an image path by stem, trying common extensions."""
    folder = Path(raw_image_folder)
    for ext in sorted(IMAGE_EXTENSIONS):
        candidate = folder / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    # Case-insensitive fallback for .JPG etc.
    if folder.is_dir():
        lower_stem = stem.lower()
        for path in folder.iterdir():
            if path.is_file() and path.stem == stem and path.suffix.lower() in IMAGE_EXTENSIONS:
                return path
            if path.is_file() and path.stem.lower() == lower_stem and path.suffix.lower() in IMAGE_EXTENSIONS:
                return path
    return None


def load_classes(class_path: str) -> List[str]:
    path = Path(class_path)
    if not path.is_file():
        raise FileNotFoundError(f"classes file not found: {class_path}")
    classes = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not classes:
        raise ValueError(f"classes file is empty: {class_path}")
    return classes


def yolo_line_to_xyxy(parts: Sequence[str], width: int, height: int) -> Tuple[int, List[int]]:
    class_idx = int(parts[0])
    x_center = float(parts[1]) * width
    y_center = float(parts[2]) * height
    box_w = float(parts[3]) * width
    box_h = float(parts[4]) * height
    x1 = int(round(x_center - box_w / 2))
    y1 = int(round(y_center - box_h / 2))
    x2 = int(round(x_center + box_w / 2))
    y2 = int(round(y_center + box_h / 2))
    # Clip to image bounds
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width - 1))
    y2 = max(0, min(y2, height - 1))
    return class_idx, [x1, y1, x2, y2]


def draw_box_on_image(
    image_stem: str,
    classes: Sequence[str],
    colors: Sequence[Sequence[int]],
    label_folder: str,
    raw_image_folder: str,
    output_image_folder: str,
) -> int:
    """Draw all YOLO boxes for one image. Returns number of boxes drawn."""
    if image_stem.startswith("."):
        return 0

    image_path = find_image_path(raw_image_folder, image_stem)
    if image_path is None:
        logger.warning("image not found for stem %r in %s", image_stem, raw_image_folder)
        return 0

    image = cv2.imread(str(image_path))
    if image is None:
        logger.warning("failed to read image: %s", image_path)
        return 0

    height, width = image.shape[:2]
    label_path = Path(label_folder) / f"{image_stem}.txt"
    box_number = 0

    if label_path.is_file():
        with label_path.open("r", encoding="utf-8") as source_file:
            for line_no, line in enumerate(source_file, start=1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    logger.warning("skip malformed label %s:%d: %r", label_path, line_no, line)
                    continue
                try:
                    class_idx, xyxy = yolo_line_to_xyxy(parts, width, height)
                except ValueError:
                    logger.warning("skip unparsable label %s:%d: %r", label_path, line_no, line)
                    continue
                if class_idx < 0 or class_idx >= len(classes):
                    logger.warning("class index %d out of range in %s:%d", class_idx, label_path, line_no)
                    continue
                plot_one_box(
                    xyxy,
                    image,
                    color=colors[class_idx],
                    label=classes[class_idx],
                    line_thickness=None,
                )
                box_number += 1
    else:
        logger.info("no label file for %s; copying image without boxes", image_stem)

    out_dir = Path(output_image_folder)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{image_stem}{image_path.suffix.lower()}"
    # Write once after all boxes are drawn (avoids per-box I/O).
    if not cv2.imwrite(str(out_path), image):
        logger.error("failed to write %s", out_path)
        return 0
    return box_number


def make_name_list(raw_image_folder: str, image_name_list_path: str) -> List[str]:
    """Collect image stems from raw_image_folder and write name_list.txt."""
    folder = Path(raw_image_folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"raw image folder not found: {raw_image_folder}")

    stems: List[str] = []
    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith("."):
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
    """Read stems one per line so names with spaces are preserved."""
    path = Path(image_name_list_path)
    if not path.is_file():
        raise FileNotFoundError(f"name list not found: {image_name_list_path}")
    with path.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle.read().split("\n") if line.strip()]


def build_colors(num_classes: int, seed: int = 42) -> List[List[int]]:
    random.seed(seed)
    return [[random.randint(0, 255) for _ in range(3)] for _ in range(num_classes)]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draw YOLO boxes on images for annotation QA.")
    parser.add_argument("--labels", default=DEFAULT_LABEL_FOLDER, help="YOLO txt label folder")
    parser.add_argument("--images", default=DEFAULT_RAW_IMAGE_FOLDER, help="Raw image folder")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_IMAGE_FOLDER, help="Output image folder")
    parser.add_argument("--classes", default=DEFAULT_CLASS_PATH, help="Class names file")
    parser.add_argument(
        "--name-list",
        default=DEFAULT_IMAGE_NAME_LIST_PATH,
        help="Path to write/read image stem list",
    )
    parser.add_argument("--seed", type=int, default=42, help="Color RNG seed")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    classes = load_classes(args.classes)
    colors = build_colors(len(classes), seed=args.seed)
    stems = make_name_list(args.images, args.name_list)
    # Re-read via newline split to match on-disk contract used by get_origin_image.
    stems = read_name_list(args.name_list)

    Path(args.output).mkdir(parents=True, exist_ok=True)

    box_total = 0
    image_total = 0
    for stem in stems:
        logger.info("processing %s", stem)
        box_num = draw_box_on_image(
            stem,
            classes,
            colors,
            args.labels,
            args.images,
            args.output,
        )
        box_total += box_num
        image_total += 1
        logger.info("boxes=%d (running boxes=%d images=%d)", box_num, box_total, image_total)

    logger.info("done: %d images, %d boxes", image_total, box_total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
