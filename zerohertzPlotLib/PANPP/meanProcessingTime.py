import os
import csv
import pandas as pd


def meanProcessingTime(dir):
    '''
    A function that averages the processing time of the model
    according to each input measured through functions such as time.time()

    [sec] -> [msec]

    ├── Model1.csv
    ├── Model2.csv
    ├── Model3.csv
    ├── ...
    └── ModelN.csv

    -> time.csv
    '''
    org = os.getcwd()
    os.chdir(dir)
    if 'time.csv' in os.listdir():
        os.remove('./time.csv')

    for i in os.listdir():
        if '.csv' in i and not i == 'time.csv':
            data = pd.read_csv(i, header=None)
            tmp = data.mean() * 1000
            with open('./time.csv', 'a', encoding='utf8') as f:
                wr = csv.writer(f)
                wr.writerow([i[0:-4], *tmp])
    os.chdir(org)