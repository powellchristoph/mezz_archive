#!/usr/bin/env python

import os
import subprocess
import sqlite3
import sys
from datetime import datetime

DATABASE = '/root/mezz_recovery/mezz.db'
ARCHIVE_ROOT = '/stornext/snfs1/VOD/Archive'
RECOVERY_DIR = 'root@HOSTNAME:/ifs/storagearray/vod/Archive/MEZZ_RESTORES'
pid_file = '/var/run/get_from_tape.pid'

def get_asset(asset):
    update_status('Running', 'start', row[0])
    print 'Starting ', asset
    cmd = "/usr/bin/rsync -av " + "\"" + ARCHIVE_ROOT + "/" + asset + "\"" + " " + RECOVERY_DIR
    print cmd
#    result = subprocess.call('ls', shell=True)
    result = subprocess.call(cmd, shell=True)
    if result == 0:
        update_status('Completed', 'completed', row[0])
        print 'Completed ', asset
    else:
        update_status('Error', 'completed', row[0])
        print 'Error ', asset

def update_status(status, type, id):
    conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    query = "UPDATE Transfers SET status='%s', %s_time='%s' WHERE id=%s;" % (status, type, datetime.now(), id)
    c.execute(query)
    conn.commit()
    c.close()

if __name__ == '__main__':

    #This is to check if there is already a lock file existing#
    if os.access(pid_file, os.F_OK):
            #if the lockfile is already there then check the PID number 
            #in the lock file
            with open(pid_file, 'r') as pd:
                old_pd = pd.readline()
            # Now we check the PID from lock file matches to the current
            # process PID
            if os.path.exists("/proc/%s" % old_pd):
                    print "You already have an instance of the program running"
                    print "It is running as process %s" % old_pd
                    sys.exit(1)
            else:
                    print "File is there but the program is not running"
                    print "Removing lock file for the: %s" % old_pd
                    os.remove(pid_file)
    
    #This is part of code where we put a PID file in the lock file
    with open(pid_file, 'w') as pd:
        pd.write("%s" % os.getpid())

    conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT id, asset FROM Transfers WHERE status=?;", ('Pending',))
    rows = c.fetchall()
    c.close()

    for row in rows:
        print 'Found asset: ', row[1]
        get_asset(row[1])

    os.remove(pid_file)
    
