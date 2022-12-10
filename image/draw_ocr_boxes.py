import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math


def draw_ocr_box_txt(image,
                     boxes,
                     txts,
                     font_path="../demo/simfang.ttf"):
    '''
        image: pillow格式的图像，
        boxes: list， list的每个元素都是 numpy.array
        [
            array([[654.,  68.],[779.,  75.],[765., 340.],[640., 333.]], dtype=float32),
            array([[524., 243.],[658., 246.],[648., 646.],[514., 642.]], dtype=float32)
        ]
        texts: list, 每个元素都是一个字符串， ['芥兰', '炒牛肉']
    '''

    h, w = image.height, image.width
    img_left = image.copy()
    img_right = Image.new('RGB', (w, h), (255, 255, 255))

    import random

    random.seed(0)
    draw_left = ImageDraw.Draw(img_left)
    draw_right = ImageDraw.Draw(img_right)
    for idx, (box, txt) in enumerate(zip(boxes, txts)):
        color = (random.randint(0, 255), random.randint(0, 255),
                 random.randint(0, 255))
        draw_left.polygon(box, fill=color)
        draw_right.polygon(
            [
                box[0][0], box[0][1], box[1][0], box[1][1], box[2][0],
                box[2][1], box[3][0], box[3][1]
            ],
            outline=color)
        box_height = math.sqrt((box[0][0] - box[3][0])**2 + (box[0][1] - box[3][
            1])**2)
        box_width = math.sqrt((box[0][0] - box[1][0])**2 + (box[0][1] - box[1][
            1])**2)
        print(box_height, box_width)
        if box_height > 2 * box_width:
            font_size = max(int(box_width * 0.8), 10)
            font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
            cur_y = box[0][1]
            for c in txt:
                char_size = font.getsize(c)
                draw_right.text(
                    (box[0][0] + 3, cur_y), c, fill=(0, 0, 0), font=font)
                cur_y += char_size[1]
        else:
            font_size = max(int(box_height * 0.8), 10)
            font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
            draw_right.text(
                [box[0][0], box[0][1]], txt, fill=(0, 0, 0), font=font)
    img_left = Image.blend(image, img_left, 0.5)
    img_show = Image.new('RGB', (w * 2, h), (255, 255, 255))
    img_show.paste(img_left, (0, 0, w, h))
    img_show.paste(img_right, (w, 0, w * 2, h))
    print(img_show.size)
    return np.array(img_show)


if __name__ == '__main__':

    boxes =[
            np.array([[654.,  68.],[779.,  75.],[765., 340.],[640., 333.]], dtype=np.float32),
            np.array([[524., 243.],[658., 246.],[648., 646.],[514., 642.]], dtype=np.float32)
            ]
    texts = ['芥兰', '炒牛肉']
    image = Image.open('../demo/000001.jpg')
    print(image.size, image.width, image.height) # w, h
    new_img = draw_ocr_box_txt(image,boxes, texts)
    new_img = cv2.cvtColor(new_img, cv2.COLOR_RGB2BGR)
    cv2.imshow('img', new_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
