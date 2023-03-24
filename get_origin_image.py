# coding:utf-8
import cv2
import os
import piexif

# Config the global variables 
RAW_IMAGE_FOLDER = './raw_images/'  # Put the original images without boxes in this folder. 检查图片存放文件夹raw_images路径
OUTPUT_IMAGE_FOLDER = './save_image/'  #The output images would be saved to this folder. 保存图片文件夹save_image路径
IMAGE_NAME_LIST_PATH = './name_list.txt'  # The file name of images will be saved into this text file. 内含有检测图片名的txt文件路径
WRONG_IMAGE_FOLDER = './wrong/'  # Put the images that you want the corresponding original images in this folder 错判图片文件夹wrong路径


def get_image(image_name, RAW_IMAGE_FOLDER, OUTPUT_IMAGE_FOLDER):
    """
    This function will get the file with the same name from RAW_IMAGE_FOLDER, and save the copy to the OUTPUT_IMAGE_FOLDER.
    """
    print(image_name)
    if image_name == '.DS_Store':
        return 0
    image_path = os.path.join(RAW_IMAGE_FOLDER, '%s.jpg' %
                              (image_name))  # 本次原始图片jpg路径

    save_file_path = os.path.join(
        OUTPUT_IMAGE_FOLDER, '%s.jpg' % (image_name))  # 本次保存图片jpg路径
    image = cv2.imread(image_path)
    cv2.imwrite(save_file_path, image)
    piexif.remove(save_file_path)


# 函数：通过保存有错判图片得文件夹，生成写有所有错判图片名称（不带后缀）得txt
def make_name_list(WRONG_IMAGE_FOLDER, IMAGE_NAME_LIST_PATH):
    """
    This function will collect the image name in the WRONG_IMAGE_FOLDER and save them in the name_list.txt. 
    """

    image_file_list = os.listdir(WRONG_IMAGE_FOLDER)  # 得到该路径下所有文件名称带后缀

    text_image_name_list_file = open(
        IMAGE_NAME_LIST_PATH, 'w')  # 以写入得方式打开txt ，方便更新 不要用追加写

    for image_file_name in image_file_list:  # 例遍写入
        image_name, file_extend = os.path.splitext(image_file_name)  # 去掉扩展命
        text_image_name_list_file.write(image_name+'\n')  # 写入

    text_image_name_list_file.close()


if __name__ == '__main__':           # 只有在文件作为脚本文件直接执行时才执行下面代码

    make_name_list(WRONG_IMAGE_FOLDER, IMAGE_NAME_LIST_PATH)  # 执行写入txt函数

    image_names = open(IMAGE_NAME_LIST_PATH).read(
    ).strip().split()  #  得到不带后缀的图片名

    image_total = 0
    for image_name in image_names:  # 遍历图片名称
        box_num = get_image(image_name, RAW_IMAGE_FOLDER, OUTPUT_IMAGE_FOLDER)
        image_total += 1
        print('Image number:', image_total)
