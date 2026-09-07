# Draw YOLO boxes

[English](README.md)

根据 YOLO 格式标注，在原图上画框，方便检查标注质量，并把错标样本对应的原图提取出来重新标注（例如用 [makesense.ai](https://www.makesense.ai/)）。

## 安装

```bash
pip install -r requirements.txt
```

`piexif` 仅在使用 `get_origin_image.py` 且需要去掉 JPEG EXIF 时用到（默认开启）。

## 用法

### 画框

1. 原图放到 `./raw_images/`（支持 `.jpg` / `.jpeg` / `.png` / `.webp` / `.bmp`）
2. YOLO txt 放到 `./labels/`（与图片同名）
3. 类别写入 `classes.txt`（每行一个）
4. 运行：

```bash
python draw_box.py
# 或指定路径：
python draw_box.py --images ./raw_images --labels ./labels --output ./save_image --classes ./classes.txt
```

结果在 `./save_image/`。每张图在画完所有框后只写入一次。

### 提取错标对应原图

1. 把画错的图放到 `./wrong/`
2. 如需干净输出可清空 `./save_image/`
3. 运行：

```bash
python get_origin_image.py
```

会按文件名（不含扩展名）从 `./raw_images/` 复制原图到 `./save_image/`。

## 说明

- 支持文件名含空格（名单按换行分割）
- 缺少 label 时会打日志，并仍保存无框图片
- 框会裁剪到图像范围内；格式错误的标注行会跳过并警告
