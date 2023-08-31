import os
import shutil
import random
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

def attach_rand_img(palette, gt, p):
    tar = random.randrange(0, len(gt))
    imgpath = 'RAW/ORG/' + gt[tar]['data']['image'][-10:]
    img = cv2.imread(imgpath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img, r = resi(img)
    palette, bias = pos(palette, img, p)
    bbox = []
    for g in gt[tar]['annotations'][0]['result']:
        coords = (r * np.array(g['value']['points']) / 100).round().astype('int32')
        coords += bias
        bbox.append(coords.tolist())
        # viz(palette, coords)
    return palette, bbox


if __name__ == "__main__":
    shutil.rmtree('SD')
    os.mkdir('SD')
    os.mkdir('SD/images')
    os.mkdir('SD/json')
    with open('asdf.json') as f:
        gt = json.load(f)
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
            palette, bb = attach_rand_img(palette, gt, p)
            for b in bb:
                tmp = {
                    "label": "###",
                    "points": [],
                    "shape_type": "polygon",
                    "flags": {}
                }
                tmp["points"] = b
                res.append(tmp)
        name = str(random.randrange(100000, 999999))
        cv2.imwrite('SD/images/' + name + '.png', palette)
        sgt["imagePath"] = name + '.png'
        for r in res:
            sgt["shapes"].append(r)
        with open('SD/json/' + name + '.json', 'w') as f:
            json.dump(sgt, f, indent=4)
