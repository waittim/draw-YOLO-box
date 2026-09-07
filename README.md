# Draw YOLO boxes

[中文](README_cn.md)

Draw bounding boxes on original images from YOLO-format annotations. Useful for checking label quality and pulling the originals of bad samples for re-annotation (e.g. with [makesense.ai](https://www.makesense.ai/)).

## Install

```bash
pip install -r requirements.txt
```

`piexif` is only needed if you use `get_origin_image.py` and want JPEG EXIF stripped (enabled by default).

## Usage

### Draw bounding boxes

1. Put raw images in `./raw_images/` (`.jpg` / `.jpeg` / `.png` / `.webp` / `.bmp`).
2. Put YOLO txt labels in `./labels/` (same stem as the image).
3. Put class names in `classes.txt` (one per line).
4. Run:

```bash
python draw_box.py
# or with custom paths:
python draw_box.py --images ./raw_images --labels ./labels --output ./save_image --classes ./classes.txt
```

Outputs go to `./save_image/`. Each image is written **once** after all boxes are drawn.

### Extract originals for wrong boxes

1. Put images with incorrect boxes into `./wrong/`.
2. Clear `./save_image/` if you want a clean output folder.
3. Run:

```bash
python get_origin_image.py
# python get_origin_image.py --wrong ./wrong --images ./raw_images --output ./save_image
```

Matching originals (by filename stem) are copied into `./save_image/`.

## Notes

- Image stems that contain spaces are supported (name lists are newline-separated).
- Missing labels log a message and still copy/save the image without boxes.
- Boxes are clipped to image bounds; malformed label lines are skipped with a warning.

## Credit

Based on [批量将yolo-v3检测结果在原图上画矩形框显示](https://blog.csdn.net/qq_32761549/article/details/90210036), with multi-label drawing, class names, safer I/O, and a helper to recover originals.
