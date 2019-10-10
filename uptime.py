import re
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
import subprocess
import sys

SSH_HOST = 'raven'
LOG_NAME = 'uptime.log'
PLOT_FORMAT = 'png'

def getLog():
    try:
        subprocess.run(['scp', '{}:{}'.format(SSH_HOST, LOG_NAME), '.'], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode

def genHourlyLoad():
    load = {}
    for i in range(24):
        load[i] = np.array([])

    with open(LOG_NAME) as file:
        for line in file:
            timestamp = ':'.join([l for l in re.split(':|,| |\n', line)[:4] if l])
            dt = datetime.strptime(timestamp, '%H:%M:%S')
            fl = float([l for l in re.split(':|,| |\n', line)[-6:] if l][2])
            load[dt.hour] = np.append(load[dt.hour], fl)

    plt.boxplot(load.values(), labels=load.keys()) # showfliers=True
    plt.savefig('load.{}'.format(PLOT_FORMAT))

if __name__ == '__main__':
    scp_code = getLog()
    if scp_code == 0:
        genHourlyLoad()
    else:
        sys.exit('Couldn\'t access uptime.log over SCP: scp exited with {}'.format(scp_code))