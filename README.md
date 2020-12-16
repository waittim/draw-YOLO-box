# draw_yolo_box

Draw bounding boxes on original images based on yolo format annotation. Help checking correctness of boxes and extract the images with wrong boxes.

## Usage

### Draw bounding boxes
1. Put all of your raw images in **raw_images** folder.
2. Put all of your annotation file(YOLO format txt) in **labels** folder.
3. Write your class information into **classes.txt**.
4. Run `python draw_box.py` in your terminal.

Now you have the images with bounding boxes in the **save_image** folder.

### Extract the corresponding raw images 
1. Put the images with incorrect boxes into **wrong** folder.
2. Clean up **save_image** folder.
3. Run `get_origin_image.py` in your terminal.
 
Now you have the raw images which have incorrect bounding boxes inside in the **save_image** folder.
