# Draw YOLO boxes

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


> Thanks for [批量将yolo-v3检测结果在原图上画矩形框显示](https://blog.csdn.net/qq_32761549/article/details/90210036). I modified the code and enhanced its ease of use, added multi-label processing and labeling of category names, and provided a method to obtain the original image.
