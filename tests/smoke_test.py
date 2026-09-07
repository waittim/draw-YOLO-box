#!/usr/bin/env python3
"""Synthetic end-to-end smoke tests for draw-YOLO-box."""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import draw_box
import get_origin_image


def write_blank(path: Path, size=(120, 160), color=(40, 40, 40)) -> None:
    img = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    img[:] = color
    assert cv2.imwrite(str(path), img)


def test_draw_space_name_multi_box_and_png(tmp: Path) -> None:
    raw = tmp / "raw_images"
    labels = tmp / "labels"
    out = tmp / "save_image"
    raw.mkdir(parents=True); labels.mkdir(parents=True); out.mkdir(parents=True)
    classes = tmp / "classes.txt"
    classes.write_text("cat\ndog\n", encoding="utf-8")

    # space in filename + png
    stem = "my photo"
    write_blank(raw / f"{stem}.png", color=(30, 30, 30))
    # 5 YOLO boxes
    lines = []
    for i, (cx, cy) in enumerate([(0.2, 0.2), (0.4, 0.4), (0.6, 0.3), (0.7, 0.7), (0.5, 0.8)]):
        lines.append(f"{i % 2} {cx} {cy} 0.2 0.2")
    (labels / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    imwrite_calls = {"n": 0}
    real_imwrite = cv2.imwrite

    def counted_imwrite(path, img, *a, **k):
        imwrite_calls["n"] += 1
        return real_imwrite(path, img, *a, **k)

    cv2.imwrite = counted_imwrite
    try:
        rc = draw_box.main([
            "--images", str(raw),
            "--labels", str(labels),
            "--output", str(out),
            "--classes", str(classes),
            "--name-list", str(tmp / "name_list.txt"),
        ])
    finally:
        cv2.imwrite = real_imwrite

    assert rc == 0, rc
    assert imwrite_calls["n"] == 1, imwrite_calls
    name_list = (tmp / "name_list.txt").read_text(encoding="utf-8")
    assert name_list.strip() == stem
    out_path = out / f"{stem}.png"
    assert out_path.is_file() and out_path.stat().st_size > 0
    # ensure whitespace split would have broken the stem
    assert "my" not in [p for p in name_list.split() if p != "my"] or True
    broken = name_list.strip().split()
    assert broken == ["my", "photo"], "control: whitespace split breaks stem"
    good = [ln for ln in name_list.split("\n") if ln.strip()]
    assert good == [stem]
    print("PASS draw: space name + 5 boxes + png + single imwrite")


def test_get_origin_space_name(tmp: Path) -> None:
    raw = tmp / "raw_images"
    wrong = tmp / "wrong"
    out = tmp / "save_image"
    raw.mkdir(parents=True); wrong.mkdir(parents=True); out.mkdir(parents=True)
    stem = "bad sample"
    write_blank(raw / f"{stem}.jpg", color=(10, 10, 200))
    write_blank(wrong / f"{stem}.jpg", color=(0, 0, 255))

    rc = get_origin_image.main([
        "--wrong", str(wrong),
        "--images", str(raw),
        "--output", str(out),
        "--name-list", str(tmp / "name_list.txt"),
        "--keep-exif",
    ])
    assert rc == 0, rc
    assert (out / f"{stem}.jpg").is_file()
    # name list newline contract
    text = (tmp / "name_list.txt").read_text(encoding="utf-8")
    assert [ln for ln in text.split("\n") if ln.strip()] == [stem]
    assert text.strip().split() == ["bad", "sample"]
    print("PASS get_origin: space name preserved")


def test_clip_and_skip_bad_lines(tmp: Path) -> None:
    raw = tmp / "raw_images"
    labels = tmp / "labels"
    out = tmp / "save_image"
    raw.mkdir(parents=True); labels.mkdir(parents=True); out.mkdir(parents=True)
    (tmp / "classes.txt").write_text("a\n", encoding="utf-8")
    write_blank(raw / "x.jpg")
    (labels / "x.txt").write_text(
        "\n".join([
            "0 0.5 0.5 2.0 2.0",  # oversized -> clipped
            "not-a-label",
            "9 0.5 0.5 0.1 0.1",  # bad class
            "0 0.3 0.3 0.1 0.1",
        ]) + "\n",
        encoding="utf-8",
    )
    n = draw_box.draw_box_on_image(
        "x",
        ["a"],
        [[0, 255, 0]],
        str(labels),
        str(raw),
        str(out),
    )
    assert n == 2, n
    assert (out / "x.jpg").is_file()
    print("PASS draw: clip + skip bad lines")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="drawyolo-smoke-") as td:
        tmp = Path(td)
        test_draw_space_name_multi_box_and_png(tmp / "t1")
        test_get_origin_space_name(tmp / "t2")
        test_clip_and_skip_bad_lines(tmp / "t3")
    print("ALL_SMOKE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
