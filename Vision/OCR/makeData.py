import os
import shutil
from glob import glob
import json
import pickle

from PIL import Image
import pandas as pd

from tqdm import tqdm


def mean(a, b, c, d, x):
    return ((3-x)*a+x*c)/3, ((3-x)*b+x*d)/3

def coord2bezier(bbox):
    c2b = bbox.reshape(-1,2).copy()
    ct = c2b.mean(0)
    pos = (c2b - ct) > 0
    for idx, (px, py) in enumerate(pos):
        if not px and not py:
            x1, y1 = c2b[idx]
        elif px and not py:
            x2, y2 = c2b[idx]
        elif px and py:
            x3, y3 = c2b[idx]
        elif not px and py:
            x4, y4 = c2b[idx]
    try:
        p1, q1 = mean(x1, y1, x2, y2, 1)
        p2, q2 = mean(x1, y1, x2, y2, 2)
        p3, q3 = mean(x3, y3, x4, y4, 1)
        p4, q4 = mean(x3, y3, x4, y4, 2)
        return [x1, y1, p1, q1, p2, q2, x2, y2, x3, y3, p3, q3, p4, q4, x4, y4]
    except:
        return []

class tokenizer():
    def __init__(self, dict_name='../dict'):
        with open(dict_name, 'rb') as f:
            dic = pickle.load(f)
        self.dic = dic
        self.len_of_dict = len(dic)
        self.token_dict = {}
        for i, d in enumerate(dic):
            self.token_dict[d] = i
        print(self.token_dict)
    def encode(self, S):
        res = [self.len_of_dict + 1 for _ in range(25)]
        for i, s in enumerate(S):
            try:
                res[i] = self.token_dict[s]
            except:
                res[i] = self.len_of_dict
        return res
    def decode(self, REC):
        S = ""
        for R in REC:
            if R == self.len_of_dict + 1:
                break
            elif R == self.len_of_dict:
                S += "[UNK]"
            else:
                S += self.dic[R]
        return S

def main(
        DATA_NAME='CustomizedData_train',
        IMG_EXT=['png', 'jpg', 'tif'],
        tar="",
        log=False,
        vis_opt=False
    ):
    JSON = DATA_NAME + '.json'
    try:
        os.remove(JSON)
    except:
        pass

    img = []
    for ie in IMG_EXT:
        img += glob(os.path.join(DATA_NAME, '*.' + ie))
    for i in img:
        os.remove(i)

    ROOT = os.path.join(DATA_NAME)
    img = []
    for ie in IMG_EXT:
        img += glob(os.path.join(ROOT, 'image', '*.' + ie))

    tok = tokenizer()
    images = []
    annotations = []
    ID = 0
    annID = 0
    LEN_BBOX = []
    LEN_REC = []
    for i in tqdm(img):
        if tar == "":
            pass
        elif tar in i:
            pass
        else:
            continue
        try:
            FILE_NAME = i.split('/')[-1]
            IMG = Image.open(i)
            try:
                rot = IMG._getexif()[274]
                if rot == 1:
                    pass
                else:
                    print("FILE_NAME:", t)
                    print("ROTATED IMAGE:", rot, i)
                    continue
            except:
                pass
            WIDTH, HEIGHT = IMG.size
            image = {
                'coco_url': '',
                'data_captured': '',
                'file_name': FILE_NAME,
                'flickr_url': '',
                'id': ID,
                'license': 0,
                'width': WIDTH,
                'height': HEIGHT
            }

            t = i.replace('image', 'txt')
            for ie in IMG_EXT:
                t = t.replace(ie, 'txt')
            gt = pd.read_csv(t, header=None, sep='\t', quoting=3)
        except Exception as e:
            print("FILE_NAME:", t)
            print("EXCEPTION:", e)
            continue

        gt = gt.to_numpy()

        LEN_BBOX.append(len(gt))
        flag = False
        tmp_annotations = []
        for g in gt:
            REC = g[8]
            if not type(REC) == str:
                print("FILE_NAME:", t)
                print("GT IS NOT STR:", g)
                flag = True
                break

            '''
            NOTE: Pre-processing of Texts
            REC = REC.replace()
            '''

            if log:
                print(REC, len(REC))
            if len(REC) > 25:
                flag = True
                break
            LEN_REC.append(len(REC))
            if not vis_opt:
                try:
                    REC = tok.encode(REC)
                except Exception as e:
                    print("FILE_NAME:", t)
                    print("EXCEPTION:", e)
                    print("LENGTH OF REC:", len(REC))
                    print(''.join(["="*20, "\n", REC, "\n", "="*20]))
                    continue
                BBOX = g[0:8]
                BBOX[[0,2,4,6]] = BBOX[[0,2,4,6]].clip(0, WIDTH)
                BBOX[[1,3,5,7]] = BBOX[[1,3,5,7]].clip(0, HEIGHT)
                if WIDTH < max(BBOX[[0,2,4,6]]) or HEIGHT < max(BBOX[[1,3,5,7]]):
                    print(WIDTH, HEIGHT, BBOX)
                    print(BBOX[[0,2,4,6]])
                    print(BBOX[[1,3,5,7]])
                BEZIER_PTS = coord2bezier(BBOX)
                if BEZIER_PTS == []:
                    break
                annID += 1
                BBOX = [min(BBOX[[0,2,4,6]]), min(BBOX[[1,3,5,7]]), max(BBOX[[0,2,4,6]]) - min(BBOX[[0,2,4,6]]), max(BBOX[[1,3,5,7]]) - min(BBOX[[1,3,5,7]])]
                BBOX = list(map(float, BBOX))
                AREA = float(BBOX[2] * BBOX[3])
                annotation = {
                    'area': AREA,
                    'category_id': 1,
                    'id': annID,
                    'image_id': ID,
                    'iscrowd': 0,
                    'bezier_pts': BEZIER_PTS, # [float]
                    'rec': REC, # [int]
                    'bbox': BBOX # [float]
                }
                if log:
                    print(tok.decode(REC))
                tmp_annotations.append(annotation)
        if flag:
            continue
        annotations += tmp_annotations
        images.append(image)
        ID += 1
        if not vis_opt:
            shutil.copy(i, os.path.join(DATA_NAME, FILE_NAME))
    if not vis_opt:
        JsonData = {
            'licenses': [],
            'info': {},
            'categories': [{'id': 1, 'name': 'text', 'supercategory': 'beverage', 'keypoints': ['mean', 'xmin', 'x2', 'x3', 'xmax', 'ymin', 'y2', 'y3', 'ymax', 'cross']}],
            'images': images,
            'annotations': annotations
        }

        with open(JSON, 'w') as f:
            json.dump(JsonData, f)
    print(max(LEN_BBOX), max(LEN_REC))
    return LEN_BBOX, LEN_REC

def vis(LEN_BBOX, LEN_REC):
    from matplotlib import pyplot as plt
    plt.rcParams['font.size'] = 20
    plt.figure(figsize=(15, 10))
    plt.hist(LEN_BBOX, bins=100)
    plt.xlabel('The number of the bbox')
    plt.ylabel('The nubmer of images')
    plt.savefig("LEN_BBOX.jpg", dpi=100, bbox_inches='tight')
    plt.figure(figsize=(15, 10))
    plt.hist(LEN_REC, bins=50)
    plt.xlabel('Length of the GT')
    plt.ylabel('The number of bboxes')
    plt.savefig("LEN_REC.jpg", dpi=100, bbox_inches='tight')
    plt.close('all')


if __name__ == "__main__":
    vis_opt = False
    if True:
        LEN_BBOX, LEN_REC = main(vis_opt=vis_opt)
        if vis_opt:
            vis(LEN_BBOX, LEN_REC)
    else:
        main('CustomizedData_test')