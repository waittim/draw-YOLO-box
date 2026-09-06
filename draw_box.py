import cv2,os,random
LABEL_FOLDER='./labels/';RAW_IMAGE_FOLDER='./raw_images/';OUTPUT_IMAGE_FOLDER='./save_image/';IMAGE_NAME_LIST_PATH='./name_list.txt';CLASS_PATH='./classes.txt'
def plot_one_box(x,image,color=None,label=None,line_thickness=None):
    tl=line_thickness or round(.002*sum(image.shape[:2])/2)+1;c1,c2=(int(x[0]),int(x[1])),(int(x[2]),int(x[3]))
    cv2.rectangle(image,c1,c2,color or [random.randint(0,255) for _ in range(3)],thickness=tl,lineType=cv2.LINE_AA)
    if label:cv2.putText(image,label,(c1[0],c1[1]-2),0,tl/3,[225,255,255],thickness=max(tl-1,1),lineType=cv2.LINE_AA)
def draw_box_on_image(image_name,classes,colors,LABEL_FOLDER,RAW_IMAGE_FOLDER,OUTPUT_IMAGE_FOLDER):
    p=os.path.join(LABEL_FOLDER,'%s.txt'%image_name)
    if image_name=='.DS_Store':return 0
    im=cv2.imread(os.path.join(RAW_IMAGE_FOLDER,'%s.jpg'%image_name))
    if im is None:return 0
    h,w=im.shape[:2];o=os.path.join(OUTPUT_IMAGE_FOLDER,'%s.jpg'%image_name);n=0
    for line in open(p) if os.path.exists(p) else []:
        a=line.split();i=int(a[0]);x,y,ww,hh=(float(v)*z for v,z in zip(a[1:5],[w,h,w,h]))
        b=[round(x-ww/2),round(y-hh/2),round(x+ww/2),round(y+hh/2)]
        plot_one_box(b,im,color=colors[i],label=classes[i],line_thickness=None);n+=1
    # Write once after all boxes are drawn (avoids per-box I/O).
    if n:cv2.imwrite(o,im)
    return n
def make_name_list(RAW_IMAGE_FOLDER,IMAGE_NAME_LIST_PATH):
    f=open(IMAGE_NAME_LIST_PATH,'w')
    for n in os.listdir(RAW_IMAGE_FOLDER):f.write(os.path.splitext(n)[0]+'\n')
    f.close()
if __name__=='__main__':
    make_name_list(RAW_IMAGE_FOLDER,IMAGE_NAME_LIST_PATH);c=open(CLASS_PATH).read().strip().split('\n');random.seed(42);cols=[[random.randint(0,255) for _ in range(3)] for _ in c]
    for n in open(IMAGE_NAME_LIST_PATH).read().strip().split('\n'):draw_box_on_image(n,c,cols,LABEL_FOLDER,RAW_IMAGE_FOLDER,OUTPUT_IMAGE_FOLDER)
