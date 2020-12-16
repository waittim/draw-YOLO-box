#coding:utf-8
import cv2
import os
import piexif

#全局变量进行路径配置
raw_images_folder = './raw_images/'  #检查图片存放文件夹raw_images路径

save_images_folder = './save_image/'  #保存图片文件夹save_image路径

name_list_path = './name_list.txt'  #里面有检测图片名称得txt文件路径

wrong_folder = './wrong/'  #错判图片文件夹wrong路径

#函数：将wrong文件夹内的对应原文件保存到save_image
def get_image(image_name,raw_images_folder,save_images_folder ):
    print(image_name)
    if image_name == '.DS_Store':
        return 0
    image_path = os.path.join( raw_images_folder,'%s.jpg'%(image_name))  #本次原始图片jpg路径
    
    save_file_path = os.path.join(save_images_folder,'%s.jpg'%(image_name)) #本次保存图片jpg路径
    image = cv2.imread(image_path)
    cv2.imwrite(save_file_path,image)
    piexif.remove(save_file_path)

    

#函数：通过保存有错判图片得文件夹，生成写有所有错判图片名称（不带后缀）得txt
def make_name_list(wrong_folder, name_list_path):

    image_file_list = os.listdir(wrong_folder) #得到该路径下所有文件名称带后缀

    text_image_name_list_file=open(name_list_path,'w')  #以写入得方式打开txt ，方便更新 不要用追加写

    for  image_file_name in image_file_list:#例遍写入
        image_name,file_extend = os.path.splitext(image_file_name)  # 去掉扩展命
        text_image_name_list_file.write(image_name+'\n') #写入
    
    text_image_name_list_file.close()


if __name__ == '__main__':           # 只有在文件作为脚本文件直接执行时才执行下面代码  

    make_name_list(wrong_folder, name_list_path) #执行写入txt函数

    image_names = open(name_list_path).read().strip().split() #得到图片名字不带后缀

    image_total = 0
    for image_name in image_names: #例遍图片名称
        box_num = get_image(image_name,raw_images_folder,save_images_folder)
        image_total += 1
        print('Image number:',image_total)
