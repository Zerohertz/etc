import os
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm


def makeResults(figname='', fontsize=20, fontfamily='Times New Roman'):
    org = os.getcwd()
    Ver = []
    opt = []
    res = {}
    col = {}
    flag = False
    os.chdir('../YOLOv5/runs/train-seg')
    for i in os.listdir():
        if os.path.isdir(i):
            try:
                tmp = pd.read_csv(i + '/results.csv')
                if not flag:
                    for j in tmp.columns:
                        col[j] = j.replace(' ', '')
                    flag = True
                res[i] = tmp.rename(columns=col).iloc[:-1, :]
                Ver.append(i)
                opt.append(i)
            except:
                continue
    os.chdir(org)
    print('='*20)
    for i, j in enumerate(opt):
        print(i, j)
    print('='*20)
    x = input()
    tmp = []
    if ',' in x:
        for i in list(map(int, x.split(','))):
            if '-----' in opt[i]:
                return
            else:
                tmp.append(Ver.index(opt[i]))
                opt[i] += '\t-----X'
    else:
        return
    plt.rcParams['font.size'] = fontsize
    plt.rcParams['font.family'] = fontfamily
    colors = {'YOLOv5n': 'red', 'YOLOv5s': 'olive', 'YOLOv5m': 'black', 'YOLOv5l': 'blue', 'YOLOv5x': 'indigo'}
    for idx in tqdm(col.values()):
        if idx != 'epoch':
            fig = plt.figure(figsize=(15, 10))
            plt.grid(True)
            for i in tmp:
                plt.plot(res[Ver[i]].loc[:, 'epoch'], res[Ver[i]].loc[:, idx], color=colors[Ver[i][0:7]], linewidth=2, label=Ver[i])
            plt.xlabel('Epoch')
            plt.ylabel(idx)
            plt.legend()
            if figname != '':
                plt.savefig(figname + '-' + idx.replace('/', '-') + '.png', dpi=300, bbox_inches='tight', pad_inches=0.3, transparent=False)
            plt.close('all')