import re
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
from subprocess import run

run(['scp', 'raven:uptime.log', '.'])

load = {}
for i in range(24):
    load[i] = np.array([])

with open('uptime.log') as file:
    for line in file:
        timestamp = ':'.join([l for l in re.split(':|,| |\n', line)[:4] if l])
        dt = datetime.strptime(timestamp, '%H:%M:%S')
        fl = float([l for l in re.split(':|,| |\n', line)[-6:] if l][2])
        load[dt.hour] = np.append(load[dt.hour], fl)

plt.boxplot([load[i] for i in range(24)], showfliers=False)
plt.savefig('load.png')