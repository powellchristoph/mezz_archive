#!/usr/bin/env python

# Author:       cpowell
# Description:  Horrible script to send out two emails with the results of the
#               mezz file migration.

import smtplib

SERVER = '192.168.21.112'
SUCCESS_TO = []
ERROR_TO = []
FROM = 'mezzmover@email.com'
SUBJECT = 'MezzMover Results'
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

# Delete any previous destination already exists entries.
with open('mezzmover.log','r') as f:
    all_lines = f.readlines()

with open('mezzmover.log', 'w') as f:
    for line in all_lines:
        if 'Destination already exists!' not in line:
            f.write(line)

success_message = """\
From: %s
To: %s
Subject: %s

%d files/%.02f GBs successfully moved.

--------------------------------------------------------------
%s
""" % (FROM, ", ".join(SUCCESS_TO), SUBJECT, total, sum, '\n'.join(results))

errors = ''
total = 0
for c in contents:
    line = c.split(',')
    if line[-1].startswith('error') and line[2] not in errors:
        total += 1
        errors += '%s: %s\n' % (line[2], line[-1])

error_message = """\
From: %s
To: %s
Subject: %s

There were %d errors!!

--------------------------------------------------------------
%s
""" % (FROM, ", ".join(ERROR_TO), SUBJECT, total, errors)

server = smtplib.SMTP(SERVER)
server.sendmail(FROM, SUCCESS_TO, success_message)
server.sendmail(FROM, ERROR_TO, error_message)
server.quit()
