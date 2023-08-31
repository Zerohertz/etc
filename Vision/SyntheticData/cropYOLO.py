import os
import random

import cv2


def yolo2crop(arr, sz):
    h, w = sz
    return int(arr[0]*w-arr[2]*w/2), int(arr[1]*h-arr[3]*h/2), int(arr[0]*w+arr[2]*w/2), int(arr[1]*h+arr[3]*h/2)

def crop_save(imgpath, sz):
    img = cv2.imread(imgpath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    a,b,c,d = yolo2crop(sz, img.shape[:-1])
    img = img[b:d, a:c, :]
    name = str(random.randrange(100000, 999999))
    cv2.imwrite(name + '.png', img)

tar = 'tar/images'
tmp = os.listdir(tar)

for i in tmp:
    imgpath = tar + '/' + i
    txtpath = tar.replace('images', 'labels') + '/' + i.replace('jpg', 'txt').replace('png', 'txt')
    with open(txtpath) as f:
        l = f.readlines()
        for j in l:
            x = list(map(float, j.strip().split()))
            crop_save(imgpath, x[1:])
