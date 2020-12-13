#coding:utf-8
import cv2
import os

#全局变量进行路径配置
text_results_folder ='/Users/waittim/Desktop/Draw_yolo/labels/'  #检测结果存放文件夹labels路径

raw_images_folder = '/Users/waittim/Desktop/Draw_yolo/raw_images/'  #检查图片存放文件夹raw_images路径

save_images_folder = '/Users/waittim/Desktop/Draw_yolo/save_image/'  #保存图片文件夹save_image路径

text_image_name_list_file_path = '/Users/waittim/Desktop/Draw_yolo/text_image_name_list.txt'  #里面有检测图片名称得txt文件路径


#函数：在一幅图片对应位置上加上矩形框  image_name 图片名称不含后缀 
def draw_a_tangle_in_one_image(image_name,text_results_folder,raw_images_folder,save_images_folder ):
    txt_path  = os.path.join(text_results_folder,'%s.txt'%(image_name))  #本次检测结果txt路径
    print(image_name)
    if image_name == '.DS_Store':
        return 0
    image_path = os.path.join( raw_images_folder,'%s.jpg'%(image_name))  #本次原始图片jpg路径
    
    save_file_path = os.path.join(save_images_folder,'%s.jpg'%(image_name)) #本次保存图片jpg路径
    
    flag_people_or_car_data = 0  #变量 代表类别
    source_file = open(txt_path)
    image = cv2.imread(image_path)
    try:
        height, width, channels = image.shape
    except:
        print('no shape info.')
        return 0

    box_number = 0
    for line in source_file: #例遍 txt文件得每一行
        staff = line.split() #对每行内容 通过以空格为分隔符对字符串进行切片
        if staff[0]== '0' :
            print('NoMask')
            flag_people_or_car_data = 1 
            
        elif staff[0]== '1' :
            print('Mask')
            flag_people_or_car_data = 2 

        x_center, y_center, w, h = float(staff[1])*width, float(staff[2])*height, float(staff[3])*width, float(staff[4])*height
        x1 = round(x_center-w/2)
        y1 = round(y_center-h/2)
        x2 = round(x_center+w/2)
        y2 = round(y_center+h/2)     
        
        if  flag_people_or_car_data == 1: 
            print(x1,y1,x2,y2,'NoMask saved')
            draw_people_tangle = cv2.rectangle(image, (x1,y1),(x2,y2),(0,0,255),2)   # 画框操作  红框  宽度为1
            cv2.imwrite(save_file_path,draw_people_tangle)  #画框 并保存
        elif  flag_people_or_car_data == 2:
            print(x1,y1,x2,y2,'Mask saved')
            draw_car_tangle = cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),2)     # 画框操作  绿框  宽度为1
            cv2.imwrite(save_file_path,draw_car_tangle)  #画框 并保存
        box_number += 1
    return box_number
    

#函数：通过保存有原始图片得文件夹，生成写有所有检测图片名称（不带后缀）得txt
def make_imageName_file_list_txt(raw_images_folder, text_image_name_list_file_path):

    image_file_list = os.listdir(raw_images_folder) #得到该路径下所有文件名称带后缀

    text_image_name_list_file=open(text_image_name_list_file_path,'w')  #以写入得方式打开txt ，方便更新 不要用追加写

    for  image_file_name in image_file_list:#例遍写入
        image_name,file_extend = os.path.splitext(image_file_name)  # 去掉扩展命
        text_image_name_list_file.write(image_name+'\n') #写入
    
    text_image_name_list_file.close()


if __name__ == '__main__':           # 只有在文件作为脚本文件直接执行时才执行下面代码  

    make_imageName_file_list_txt(raw_images_folder, text_image_name_list_file_path) #执行写入txt函数

    image_names = open(text_image_name_list_file_path).read().strip().split() #得到图片名字不带后缀

    box_total = 0
    image_total = 0
    for image_name in image_names: #例遍图片名称
        box_num = draw_a_tangle_in_one_image(image_name,text_results_folder,raw_images_folder,save_images_folder)#对图片画框
        box_total += box_num
        image_total += 1
        print('Box number:', box_total, 'Image number:',image_total)
