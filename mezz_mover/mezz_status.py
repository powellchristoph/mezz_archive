#!/usr/bin/env python

# Author:       cpowell

from datetime import datetime as dt

log_file = '/root/bin/mezzmover.log'

with open(log_file, 'r') as lf:
    contents = lf.read().splitlines()

results = []
sum = 0
total = 0
for c in contents:
    line = c.split(',')
    if line[-1] == 'success':
        sum += float(line[1])
        total += 1
        results.append('%s  - %s' % (line[0], line[3]))

now = dt.now()
print '{0} : Total {1:.2f} GB copied.'.format(now, sum)
