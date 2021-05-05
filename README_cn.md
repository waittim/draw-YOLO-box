# Draw YOLO boxes
[\[English\]](https://github.com/waittim/draw_yolo_box/blob/main/README.md)

基于YOLO格式标注文件，在原图片上画出标记框。可帮助检查标注的正确性，并将含有错标的原图像取出，您可以使用[makesense.ai](https://www.makesense.ai/)等工具重新进行标注。


## 用法

### 绘制标记框
1. 将所有原始图片放入`./raw_images/`文件夹。
2. 将所有标注文件（YOLO格式txt）放入`./labels/`文件夹。
3. 将你的类别信息写入**classes.txt**，依次每个一行。
4. 在terminal中运行`python draw_box.py`。

所有画出了标记框的图片现已被存至`./save_image/`文件夹。

### 提取相应原始图片
1. 将含有错标的图片放入`./wrong/`文件夹.
2. 清空`./save_image/`文件夹.
3. 在terminal中运行`python get_origin_image.py`。
 
所有对应的原始图片现已被存至`./save_image/`文件夹。

## 其他

> 感谢[批量将yolo-v3检测结果在原图上画矩形框显示](https://blog.csdn.net/qq_32761549/article/details/90210036)提供的框架。在此基础上我改进了易用性，增加了对多类别标签的处理与标注，并增加了提取原图片的功能。 
