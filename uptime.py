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
HISTORY_SMOOTHING = 4

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
    plt.boxplot(load.values(), labels=load.keys()) # showfliers=True
    plt.savefig('hourly.{}'.format(PLOT_FORMAT))

def genLoadHistory(splitLines=None):
    if splitLines is None:
        splitLines = genSplitLines()
    history = np.zeros(SAMPLES_PER_WEEK)
    lines = [float([l for l in line[-6:] if l][2]) for line in splitLines]

    for i in range(len(lines)):
        start = max(0, i - HISTORY_SMOOTHING)
        band = lines[start:i + 1]
        history[i - len(lines)] = np.mean(band)

    plt.figure()
    plt.plot(np.arange(0, 7, 7 / SAMPLES_PER_WEEK), history)
    plt.savefig('history.{}'.format(PLOT_FORMAT))

if __name__ == '__main__':
    scp_code = getLog()
    if scp_code == 0:
        splitLines = genSplitLines()
        genHourlyLoad(splitLines)
        genLoadHistory(splitLines)
    else:
        sys.exit('Couldn\'t access uptime.log over SCP: scp exited with {}'.format(scp_code))