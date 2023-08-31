import os
from glob import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def CLEvalPlot(time_dir, figname='', fontsize=20, fontfamily='Times New Roman',
               yl=[98, 99]):
    '''
    Visualization of HMean, Precision, Recall calculated through CLEval (https://github.com/clovaai/CLEval)
    and processing time calculated through zerohertzPlotLib.meanProcessingTime()
    '''
    plt.rcParams['font.size'] = fontsize
    plt.rcParams['font.family'] = fontfamily
    org = os.getcwd()
    os.chdir(time_dir)
    if 'time' in time_dir:
        data = pd.read_csv('./time.csv', header=None)
        K = data[0][:]
        N = len(K)
        Ver = ['' for _ in range(N)]
        Time = [[0 for _ in range(N)] for _ in range(1)]
        Met = [[0 for _ in range(N)] for _ in range(3)]
        for i in range(N):
            Time[0][i] = data[1][i]
        for i in range(N):
            try:
                data = pd.read_csv('../evaluation/' + K[i] + '.csv', header=None)
                for j in range(3):
                    Met[j][i] = data[j+1][0]
            except:
                Ver[i] += '\t-----X'
                continue
        for i in range(N):
            Ver[i] = K[i].replace('_', ' ')
        tmp = []
        opt = []
        for v in Ver:
            opt.append(v)
        print('='*20)
        for i, j in enumerate(opt):
            print(i, j)
        print('='*20)
        x = input()
        if ',' in x:
            for i in list(map(int, x.split(','))):
                if '-----' in opt[i]:
                    os.chdir(org)
                    return
                else:
                    tmp.append(Ver.index(opt[i]))
                    opt[i] += '\t-----X'
        else:
            os.chdir(org)
            return
        print("Plotting...")
        N = len(tmp)
        Met, Time = np.array(Met), np.array(Time)
        Ver, Met, Time = [Ver[i] for i in tmp], Met[:,tmp], Time[:,tmp]
        idx = np.arange(N) * 4 # 0 ~ 4X(N-1)
        bar_width = 1
        fig = plt.figure(figsize=(15, 10))
        plt.subplot(2,1,1)
        plt.grid(True)
        fig.set_facecolor('white')
        plt.bar(idx - bar_width, Met[0], bar_width, label='HMean', color='black', zorder=10)
        plt.bar(idx, Met[1], bar_width, label='Precision', color='red', zorder=10)
        plt.bar(idx + bar_width, Met[2], bar_width, label='Recall', color='blue', zorder=10)
        plt.xticks(idx, Ver, rotation=0)
        plt.xlim([-N/1.2, 4*(N - 1) + N/1.2])
        plt.ylabel('[%]')
        plt.ylim(yl)
        plt.legend(loc='upper right', bbox_to_anchor=(1.21, 1.02))
        plt.subplot(2,1,2)
        plt.grid(True)
        plt.bar(idx, Time[0], label='Total\nprocessing\ntime', color='olive', zorder=10)
        plt.xticks(idx, Ver, rotation=0)
        plt.xlim([-N/1.2, 4*(N - 1) + N/1.2])
        plt.ylim([0, 170])
        plt.ylabel('Time [ms]')
        plt.legend(loc='upper right', bbox_to_anchor=(1.21, 1.02))
        os.chdir(org)
        res = [[] for _ in range(4)]
        for i in range(3):
            res[i].append('{:.3f} [%]'.format(Met[i][0]))
            res[i].append('{:.3f} [%]'.format(Met[i][-1]))
            res[i].append('{:.3f} [%p]'.format(Met[i][-1] - Met[i][0], 2))
            res[i].append('{:.3f} [%]'.format((Met[i][-1] - Met[i][0]) / Met[i][0] * 100, 2))
        res[3].append('{:.3f} [ms]'.format(Time[0][0]))
        res[3].append('{:.3f} [ms]'.format(Time[0][-1]))
        res[3].append('{:.3f} [ms]'.format(Time[0][-1] - Time[0][0]))
        res[3].append('{:.3f} [%]'.format((Time[0][-1] - Time[0][0]) / Time[0][0] * 100))
        print('||HMean|Precision|Recall|Time|')
        print('|:-:|:-:|:-:|:-:|:-:|')
        col = [Ver[0], Ver[-1], 'Difference', 'Percentage']
        for i in range(len(res[0])):
            print('|' + col[i] + '|', end='')
            for j in range(len(res)):
                print(res[j][i], end='|')
            print()
        if figname != '':
            print("Saving...")
            plt.savefig(figname + '.png', dpi=300, bbox_inches='tight', pad_inches=0.3, transparent=False)
    else:
        K = glob('*.csv')
        N = len(K)
        Ver = ['' for _ in range(N)]
        Met = [[0 for _ in range(N)] for _ in range(3)]
        for i in range(N):
            try:
                data = pd.read_csv(K[i], header=None)
                for j in range(3):
                    Met[j][i] = data[j+1][0]
            except:
                K[i] += '\t-----X'
                continue
        for i in range(N):
            Ver[i] = K[i].replace('_', ' ').replace('.csv', '')
        tmp = []
        opt = []
        for v in Ver:
            opt.append(v)
        print('='*20)
        for i, j in enumerate(opt):
            print(i, j)
        print('='*20)
        x = input()
        if ',' in x:
            for i in list(map(int, x.split(','))):
                if '-----' in opt[i]:
                    os.chdir(org)
                    return
                else:
                    tmp.append(Ver.index(opt[i]))
                    opt[i] += '\t-----X'
        else:
            os.chdir(org)
            return
        print("Plotting...")
        N = len(tmp)
        Met = np.array(Met)
        Ver, Met = [Ver[i] for i in tmp], Met[:,tmp]
        idx = np.arange(N) * 4 # 0 ~ 4X(N-1)
        bar_width = 1
        fig = plt.figure(figsize=(15, 10))
        plt.grid(True)
        fig.set_facecolor('white')
        plt.bar(idx - bar_width, Met[0], bar_width, label='HMean', color='black', zorder=10)
        plt.bar(idx, Met[1], bar_width, label='Precision', color='red', zorder=10)
        plt.bar(idx + bar_width, Met[2], bar_width, label='Recall', color='blue', zorder=10)
        plt.xticks(idx, Ver, rotation=0)
        plt.xlim([-N/1.2, 4*(N - 1) + N/1.2])
        plt.ylabel('[%]')
        plt.ylim(yl)
        plt.legend(loc='upper right', bbox_to_anchor=(1.21, 1.02))
        os.chdir(org)
        res = [[] for _ in range(3)]
        for i in range(3):
            res[i].append('{:.3f} [%]'.format(Met[i][0]))
            res[i].append('{:.3f} [%]'.format(Met[i][-1]))
            res[i].append('{:.3f} [%p]'.format(Met[i][-1] - Met[i][0], 2))
            res[i].append('{:.3f} [%]'.format((Met[i][-1] - Met[i][0]) / Met[i][0] * 100, 2))
        print('||HMean|Precision|Recall|')
        print('|:-:|:-:|:-:|:-:|')
        col = [Ver[0], Ver[-1], 'Difference', 'Percentage']
        for i in range(len(res[0])):
            print('|' + col[i] + '|', end='')
            for j in range(len(res)):
                print(res[j][i], end='|')
            print()
        if figname != '':
            print("Saving...")
            plt.savefig(figname + '.png', dpi=300, bbox_inches='tight', pad_inches=0.3, transparent=False)