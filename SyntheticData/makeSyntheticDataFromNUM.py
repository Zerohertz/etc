import os
import shutil
import random
from glob import glob
import json
import numpy as np
import cv2
from tqdm import tqdm


def viz(palette, coords):
    s = [0, 1, 2, 3]
    e = [1, 2, 3, 0]
    for i, j in zip(s, e):
        cv2.line(palette, coords[i], coords[j], (0, 0, 255), 2)

def pos(palette, img, p):
    w, h, _ = img.shape
    for i in range(4):
        p[i] = int(p[i])
    tarw, tarh = random.randrange(p[0], p[2] - w), random.randrange(p[1], p[3] - h)
    palette[tarw:tarw+w, tarh:tarh+h, :] = img
    return palette, np.array((tarh, tarw)).astype('int32')

def resi(img):
    w, h = img.shape[:-1]
    rs = random.randrange(500, 900)
    if h < w:
        img = cv2.resize(img, (int(rs*h/w), rs))
    else:
        img = cv2.resize(img, (rs, int(rs*w/h)))
    w, h = img.shape[:-1]
    r = np.array((h, w))
    return img, r

def makeNum(palette, pw, ph):
    angle = -90
    M = cv2.getRotationMatrix2D((pw // 2, ph // 2), angle, 1.0)
    palette = cv2.warpAffine(palette, M, (pw, ph))
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    angle = 90
    M = cv2.getRotationMatrix2D((pw // 2, ph // 2), angle, 1.0)
    bbox = []
    text = []
    bias = 5
    for _ in range(20):
        t = str(random.randrange(1, 900)) + ' , ' + str(random.randrange(100, 900))
        text.append(t.replace(' ', ''))
        ((tw, th), _) = cv2.getTextSize(t, font, font_scale, thickness)
        tarw, tarh = random.randrange(pw - tw), random.randrange(ph - th)
        cv2.putText(palette, t, (tarw, tarh), font, font_scale, (0, 0, 0), thickness)
        inb = [[tarw-bias, tarh+bias],[tarw+tw+bias, tarh+bias],[tarw+tw+bias, tarh-th-bias],[tarw-bias, tarh-th-bias]]
        outb = []
        for b in inb:
            pt = np.array([b[0], b[1], 1])
            b = M@pt
            outb.append(b.round().astype('int32').tolist())
        bbox.append(outb)
    palette = cv2.warpAffine(palette, M, (pw, ph))
    return palette, bbox, text

def attach_rand_img(palette, gt, p):
    tar = random.randrange(0, len(gt))
    imgpath = gt[tar]
    img = cv2.imread(imgpath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img, _ = resi(img)
    palette, _ = pos(palette, img, p)
    return palette


if __name__ == "__main__":
    shutil.rmtree('SD')
    os.mkdir('SD')
    os.mkdir('SD/images')
    os.mkdir('SD/json')
    gt = glob('RAW/ORG/*.png')
    pw, ph = 3000, 3000
    pp = []
    sq = 3
    for i in range(sq):
        for j in range(sq):
            pp.append([i/sq * pw, j/sq * ph, (i+1)/sq * pw, (j+1)/sq * ph])
    for i in tqdm(range(1000)):
        sgt = {
            "version": "5.0.5",
            "flags": {},
            "shapes": [],
            "imagePath": "",
            "imageHeight": ph,
            "imageWidth": pw
        }
        res = []
        palette = np.full((pw,ph,3), 255, np.uint8)
        for p in pp:
            palette = attach_rand_img(palette, gt, p)
        palette, bb, tt = makeNum(palette, pw, ph)
        for b, t in zip(bb, tt):
            viz(palette, b)
            tmp = {
                "label": "###",
                "points": [],
                "shape_type": "polygon",
                "flags": {}
            }
            tmp["label"] = t
            tmp["points"] = b
            res.append(tmp)
        name = str(random.randrange(100000, 999999))
        cv2.imwrite('SD/images/' + name + '.png', palette)
        sgt["imagePath"] = name + '.png'
        for r in res:
            sgt["shapes"].append(r)
        with open('SD/json/' + name + '.json', 'w') as f:
            json.dump(sgt, f, indent=4)