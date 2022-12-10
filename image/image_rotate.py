import cv2
import numpy as np
from PIL import Image
import math
import time

def time_cost(fn):
    def _wrapper(*args, **kwargs):
        start = time.time()
        fn_result = fn(*args, **kwargs)
        print("%s cost %s second" % (fn.__name__, time.time() - start))
        return fn_result
    return _wrapper

@time_cost
def rotate_img(img, angle):
    '''
    利用wrapffine实现图像逆时针旋转
    Args:
        img: np.array format image
        angle: rotate angle such as 45, 90

    Returns:
        旋转后的图像
    '''


    img_cv_h, img_cv_w, _ = img.shape

    # 第一个参数旋转中心，第二个参数旋转角度，第三个参数缩放比例， 获取旋转矩阵
    m1 = cv2.getRotationMatrix2D((img_cv_w/2, img_cv_h/2), angle, 1)
    #print(m1)
    # 旋转后图像尺寸的计算
    heightNew = int(img_cv_w * abs(math.sin(angle * math.pi / 180.0)) + img_cv_h * abs(math.cos(angle * math.pi / 180.0)))
    widthNew = int(img_cv_w * abs(math.cos(angle * math.pi / 180.0)) + img_cv_h * abs(math.sin(angle * math.pi / 180.0)))
    #print(widthNew, heightNew)
    # 新的旋转矩阵m1
    m1[0,2] += (widthNew - img_cv_w ) / 2
    m1[1,2] += (heightNew - img_cv_h)/ 2
    # print(m1)
    res1 = cv2.warpAffine(img, m1, (widthNew, heightNew))
    return res1


if __name__ == '__main__':



    img_path = '../demo/000001.jpg'
    img = cv2.imread(img_path)

    # print(img.shape)  # (720, 1280, 3) h,w,c
    # 图像的x对应的是w， y对应的是h
    # img = cv2.resize(img, (640, 360))
    angle = 45
    new_img = rotate_img(img, angle)

    cv2.imshow('img', new_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
