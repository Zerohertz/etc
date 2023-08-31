import os
import cv2
import matplotlib.pyplot as plt


def printRes(output_dir):
    '''
    A function for printing result image names
    '''
    org = os.getcwd()
    os.chdir(output_dir)
    tmp = os.listdir()
    res = []
    for i in sorted(tmp):
        if ('.jpg' in i) or ('.jpeg' in i) or ('.png' in i) or ('.tif' in i):
            print(i)
            res.append(i)
    os.chdir(org)
    return res


def diffRes(output_dir, img, Ver, cut=[], tensor='', figname='',
            fontsize=20, fontfamily='Times New Roman', res=100):
    '''
    A function for comparing results of computer vision models
    '''
    plt.rcParams['font.size'] = fontsize
    plt.rcParams['font.family'] = fontfamily
    fig = plt.figure(figsize=(15, 15))
    fig.set_facecolor('white')
    for i, j in enumerate(Ver):
        if len(Ver) == 2:
            plt.subplot(1,2,i+1)
        elif 2 < len(Ver) <= 4:
            plt.subplot(2,2,i+1)
        elif 4 < len(Ver) <= 6:
            plt.subplot(3,2,i+1)
        else:
            return
        tmp = plt.imread(os.path.join(output_dir, j, tensor, img))
        if i == 0:
            w, h, _ = tmp.shape
        if tmp.shape[0] != w or tmp.shape[1] != h:
            tmp = cv2.resize(tmp, (h, w))
        if cut == []:
            plt.imshow(tmp)
        else:
            plt.imshow(tmp[cut[0]:cut[0]+cut[2],cut[1]:cut[1]+cut[3],:])
        plt.title(j.replace('_', ' '))
        plt.axis('off')
    if figname != '':
        plt.savefig(figname + '.png', dpi=res, bbox_inches='tight', pad_inches=0.3, transparent=False)
        plt.close('all')