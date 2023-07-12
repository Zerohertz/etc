# gpu_memory_logger.sh

```shell
chmod +x gpu_memory_logger.sh
./gpu_memory_logger.sh
```

[8번 줄](https://github.com/Zerohertz/etc/blob/master/.sh/gpu_memory_logger.sh#L8)에 GPU의 index를 지정하여 매 시간마다의 메모리를 `.txt`로 저장

<details>
<summary>
시각화를 위한 python 코드
</summary>

```python monitoring.py
import time
from glob import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def set_start_time(tar):
    for tmp in tar:
        data = pd.read_csv(tmp).to_numpy()
        try:
            mst = min(mst, np.datetime64(data[0,0]))
        except:
            mst = np.datetime64(data[0,0])
    return mst

def ts2rt(data, start_time):
    timestamps = [np.datetime64(ts) for ts in data[:, 0]]
    return [(ts - start_time) / np.timedelta64(1, 's') for ts in timestamps]

def renewal(pos, start_time):
    data = pd.read_csv(pos).to_numpy()
    x = ts2rt(data, start_time)
    y = data[:, 1]
    plt.plot(x, y, linewidth=2, label=pos.split('/')[-1].split('.')[0].upper())
    return x

def init_plt():
    plt.figure(figsize=(15, 10))
    plt.grid(True)
    plt.xlabel('Time [sec]')
    plt.ylabel('GPU Memory [MiB]')

def done_plt(THRESHOLD):
    plt.ylim([-10, THRESHOLD + THRESHOLD/20])
    plt.legend()
    plt.savefig('tmp.png', dpi=100, bbox_inches='tight')
    plt.close('all')

def main(tar, mst):
    THRESHOLD = 32768
    init_plt()
    x = []
    for tmp in tar:
        x_ = renewal(tmp, mst)
        if len(x) < len(x_):
            x = x_
    plt.plot(x, np.ones(len(x)) * THRESHOLD, linewidth=3, label='THRESHOLD')
    done_plt(THRESHOLD)

if __name__ == "__main__":
    plt.rcParams['font.size'] = 20
    plt.rcParams['font.family'] = 'Times New Roman'

    tar = glob("gpu_memory_usage_*.txt")
    tar.sort()

    mst = set_start_time(tar)

    while True:
        main(tar, mst)
        time.sleep(1)
```
![tmp](https://github.com/Zerohertz/Zerohertz/assets/42334717/fd0c75ee-e627-4131-852e-cef87be8fc7e)
</details>
