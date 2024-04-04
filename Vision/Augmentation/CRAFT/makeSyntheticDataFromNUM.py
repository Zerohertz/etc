import os
import shutil
import random
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from tqdm import tqdm


def pos(palette, img, p):
    w, h, _ = img.shape
    for i in range(4):
        p[i] = int(p[i])
    tarw, tarh = random.randrange(p[0], p[2] - w), random.randrange(p[1], p[3] - h)
    palette[tarw:tarw+w, tarh:tarh+h, :] = img
    return palette, np.array((tarh, tarw)).astype('int32')

def resi(img):
    w, h = img.shape[:-1]
    rs = random.randrange(50, 120)
    if h < w:
        img = cv2.resize(img, (int(rs*h/w), rs))
    else:
        img = cv2.resize(img, (rs, int(rs*w/h)))
    w, h = img.shape[:-1]
    r = np.array((h, w))
    return img, r

def coords2bbox(coord):
    xm = min(coord[0][0], coord[1][0], coord[2][0], coord[3][0])
    xM = max(coord[0][0], coord[1][0], coord[2][0], coord[3][0])
    ym = min(coord[0][1], coord[1][1], coord[2][1], coord[3][1])
    yM = max(coord[0][1], coord[1][1], coord[2][1], coord[3][1])
    return xm, xM, ym, yM

def attach_rand_img(palette, gt, p):
    tar = random.randrange(0, len(gt))
    imgpath = 'RAW/ORG/' + gt[tar]['data']['image'][-10:] #gt[tar]
    img = cv2.imread(imgpath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img, r = resi(img)
    palette, bias = pos(palette, img, p)
    for g in gt[tar]['annotations'][0]['result']:
        coords = (r * np.array(g['value']['points']) / 100).round().astype('int32')
        coords += bias
        a,b,c,d = coords2bbox(coords)
        palette[c:d,a:b,:] = 255
    return palette

def viz(palette, coords):
    s = [0, 1, 2, 3]
    e = [1, 2, 3, 0]
    for i, j in zip(s, e):
        cv2.line(palette, coords[i], coords[j], (0, 0, 255), 2)

def makeNum(palette, p, ang):
    pw, ph = palette.shape[:-1]
    angle = -1 * ang
    M = cv2.getRotationMatrix2D((pw // 2, ph // 2), angle, 1.0)
    pn = [0, 0, 0 ,0]
    pt = np.array([p[0], p[1], 1])
    pn[:2] = (M@pt).round().astype('int32')
    pt = np.array([p[2], p[3], 1])
    pn[2:] = (M@pt).round().astype('int32')
    if pn[0] > pn[2]:
        tmp = pn[0]
        pn[0] = pn[2]
        pn[2] = tmp
    if pn[1] > pn[3]:
        tmp = pn[1]
        pn[1] = pn[3]
        pn[3] = tmp
    palette = cv2.warpAffine(palette, M, (pw, ph))
    bbox = []
    text = []
    t = str(random.randrange(1, 999)) + ',' + str(random.randrange(900, 999))
    text.append(t)
    palette = Image.fromarray(palette)
    draw = ImageDraw.Draw(palette)
    font = ImageFont.truetype('Kosugi-Regular.ttf', 15)
    tw, th = draw.textsize(t, font=font)
    bias = 30
    tarw, tarh = random.randrange(bias + pn[0], pn[2] - tw - bias), random.randrange(bias + pn[1], pn[3] - th - bias)
    draw.text((tarw, tarh), t, font=font, fill=(0,0,0,0))
    palette = np.array(palette)
    # coords = [[pn[0]+bias,pn[1]+bias], [pn[0]+bias,pn[3]-bias], [pn[2]-bias,pn[3]-bias], [pn[2]-bias,pn[1]+bias]]
    # viz(palette, coords)
    bias = 5
    inb = [[tarw-bias, tarh-bias],[tarw+tw+bias, tarh-bias],[tarw+tw+bias, tarh+th+bias],[tarw-bias, tarh+th+bias]]
    outb = []
    angle = ang
    M = cv2.getRotationMatrix2D((pw // 2, ph // 2), angle, 1.0)
    for b in inb:
        pt = np.array([b[0], b[1], 1])
        b = M@pt
        outb.append(b.round().astype('int32').tolist())
    bbox.append(outb)
    palette = cv2.warpAffine(palette, M, (pw, ph))
    return palette, bbox, text


if __name__ == "__main__":
    shutil.rmtree('SD')
    os.mkdir('SD')
    os.mkdir('SD/images')
    os.mkdir('SD/json')
    with open('asdf.json') as f:
        gt = json.load(f)
    pw, ph = 1000, 1000
    pp = []
    sq = 8
    for i in range(sq):
        for j in range(sq):
            pp.append([i/sq * pw, j/sq * ph, (i+1)/sq * pw, (j+1)/sq * ph])
    for i in tqdm(range(500)):
        sgt = {
            "version": "5.0.5",
            "flags": {},
            "shapes": [],
            "imagePath": "",
            "imageHeight": ph,
            "imageWidth": pw
        }
        res, bb, tt = [], [], []
        palette = np.full((pw,ph,3), 255, np.uint8)
        for p in pp:
            palette = attach_rand_img(palette, gt, p)
        for j, p in enumerate(pp):
            if j % 3 == 0:
                palette, b, t = makeNum(palette, p, 90)
            elif j % 3 == 1:
                palette, b, t = makeNum(palette, p, -90)
            elif j % 3 == 2:
                palette, b, t = makeNum(palette, p, 0)
            bb += b
            tt += t
            # break
        for b, t in zip(bb, tt):
            # viz(palette, b)
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
        with open('SD/json/' + name + '.json', 'w', encoding='utf-8') as f:
            json.dump(sgt, f, indent=4)