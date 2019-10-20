import re
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
import subprocess
import sys

SSH_HOST = 'raven'
LOG_NAME = 'uptime.log'
PLOT_FORMAT = 'png'
SAMPLES_PER_WEEK = 672
HISTORY_SMOOTHING_FINE = 4
HISTORY_SMOOTHING_COARSE = HISTORY_SMOOTHING_FINE * 8

def getLog():
    try:
        subprocess.run(['scp', '{}:{}'.format(SSH_HOST, LOG_NAME), '.'], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode

def genSplitLines():
    with open(LOG_NAME) as file:
        return [re.split(':|,| |\n', line) for line in file]

def genHourlyLoad(splitLines=None):
    load = {}
    for i in range(24):
        load[i] = np.array([])

    if splitLines is None:
        splitLines = genSplitLines()
    if len(splitLines) > SAMPLES_PER_WEEK:
        splitLines = splitLines[-SAMPLES_PER_WEEK:]
    for line in splitLines:
        timestamp = ':'.join([l for l in line[:4] if l])
        dt = datetime.strptime(timestamp, '%H:%M:%S')
        fl = float([l for l in line[-6:] if l][2])
        load[dt.hour] = np.append(load[dt.hour], fl)

    plt.figure()
    plt.boxplot(load.values(), labels=load.keys())
    plt.title('Load per hour over past 7 days')
    plt.xlabel('hour')
    plt.ylabel('average load')
    plt.savefig('hourly.{}'.format(PLOT_FORMAT))

def genLoadHistory(splitLines=None):
    if splitLines is None:
        splitLines = genSplitLines()
    lines = [float([l for l in line[-6:] if l][2]) for line in splitLines[-SAMPLES_PER_WEEK:]]
    history_fine = np.zeros(SAMPLES_PER_WEEK)
    history_coarse = np.zeros(SAMPLES_PER_WEEK)

    for i in range(len(lines)):
        start_fine = max(0, i - HISTORY_SMOOTHING_FINE)
        band_fine = lines[start_fine:i + 1]
        history_fine[i - len(lines)] = np.mean(band_fine)
        start_coarse = max(0, i - HISTORY_SMOOTHING_COARSE)
        band_coarse = lines[start_coarse:i + 1]
        history_coarse[i - len(lines)] = np.mean(band_coarse)

    plt.figure()
    x = np.arange(7, 0, -7 / SAMPLES_PER_WEEK)
    plt.plot(x, history_fine, color='#ffcccc')
    plt.plot(x, history_coarse, color='#ff0000')
    plt.gca().invert_xaxis()
    plt.title('Averaged load over past 7 days')
    plt.xlabel('days ago')
    plt.ylabel('average load')
    plt.savefig('history.{}'.format(PLOT_FORMAT))

if __name__ == '__main__':
    scp_code = getLog()
    if scp_code == 0:
        splitLines = genSplitLines()
        genHourlyLoad(splitLines)
        genLoadHistory(splitLines)
    else:
        sys.exit('Couldn\'t access uptime.log over SCP: scp exited with code {}'.format(scp_code))
