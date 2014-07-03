#!/usr/bin/env python

# Author:       Chris Powell
# Description:  Script to move files from the isislon storage to the new stornext.
#               It makes all attempts to move as safely as possible and will error 
#               on nearly everything just to be safe. Logs the output.

import datetime
import os
import sys
import shutil
import signal
import time
import multiprocessing

class FileMover(multiprocessing.Process):
    def __init__(self, queue, log_queue):
        multiprocessing.Process.__init__(self)
        self.file_queue = queue
        self.logger = log_queue
        self.format = '%Y-%m-%d %H:%M:%S'

    def run(self):
        while True:
            self.source, self.dest = self.file_queue.get()

            if self.source is None or self.dest is None:
                self.file_queue.task_done()
                break
    
            if os.path.exists(self.dest):
                msg = "%s,0,%s,%s,error - Destination already exists!" % (datetime.datetime.now().strftime(self.format), self.source, self.dest)
                self.logger.put(msg)
                self.file_queue.task_done()
                continue
            # Check if the files are stable
            elif not self.is_stable(self.source):
                print '%s is not stable, skipping...' % self.source
                self.file_queue.task_done()
                continue
            # Everything is good, move the file
            else:
                self.move()
                self.file_queue.task_done()
        return

    def move(self):
#        size = sum([os.path.getsize(os.path.join(self.source, f)) for f in os.listdir(self.source)])/1024.0/1024.0/1024.0
        size = self.get_size(self.source)
        # Copy the file
        try:
            print 'Copying %s to %s' % (self.source, self.dest)
            shutil.copytree(self.source, self.dest)
            msg = "%s,%.02f,%s,%s,success" % (datetime.datetime.now().strftime(self.format), size, self.source, self.dest)
            self.logger.put(msg)
            success = True
        except Exception as err:
            msg = "%s,%.02f,%s,%s,error - %s" % (datetime.datetime.now().strftime(self.format), size, self.source, self.dest, str(err))
            self.logger.put(msg)
            success = False

        # Copy was good, remove the source
        if success == True:
            try:
                shutil.rmtree(self.source)
                print 'Removing %s' % self.source
            except Exception as err:
                msg = "%s,%.02f,%s,error - %s" % (datetime.datetime.now().strftime(self.format), size, self.source, str(err))
                self.logger.put(msg)
        else:
            msg = "%s,%.02f,%s,%s,error - Copy was not successful, leaving source." % (datetime.datetime.now().strftime(self.format), size, self.source, self.dest)
            self.logger.put(msg)

        return

    def get_size(self, start_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size/1024.0/1024.0/1024.0
    
    def is_stable(self, source):
        ''' Checks that the given source is stable and that there is no file system activity. 
        Does not do recursive checks on directories! '''

        # If source is a file
        if os.path.isfile(source):
            f = open(source, 'rb')
            f.seek(0,2)
            lb1 = f.tell()
            f.close()
 
            time.sleep(5)
 
            f = open(source, 'rb')
            f.seek(0,2)
            lb2 = f.tell()
            f.close()
            if lb1 != lb2:
                return False
            else:
                return True
 
        # If source is a directory
        elif os.path.isdir(source):
            file_list = [os.path.join(source, f) for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]

            # If empty dir, skip
            if not file_list:
                return True
 
            # Get the last byte of each file in the file_list
            eof = {}
            for file_name in file_list:
                f = open(file_name, 'rb')
                f.seek(0,2)
                eof[file_name] = f.tell()
                f.close()
 
            time.sleep(5)
 
            # Return False if any new files were created during our sleep
            second_file_list = [os.path.join(source, f) for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
            if file_list != second_file_list:
                return False
 
            # Return false if the previous last byte of the file does not match the existing last byte
            for file_name in file_list:
                f = open(file_name, 'rb')
                f.seek(0,2)
                lb = f.tell()
                f.close()
                if lb != eof[file_name]:
                    return False
            
            # Everything passed!
            return True                                                                                                
 
        # Don't know what we got, so quit
        else:
            return False

def log_it(log_queue, log_file):
    while True:
        if not log_queue.empty():
            with open(log_file, 'a') as fh:
                msg = log_queue.get()
                if msg is None:
                    break
                else:
                    fh.write(msg + '\n')
    return

if __name__ == '__main__':

#    source_dir = '/root/bin/archive'
#    dest_dir = '/stornext/snfs1/cpowell-test/new_archive'
    source_dir = '/mnt/isilon_archive'
    dest_dir = '/stornext/snfs1/VOD/Archive'
    log_file = '/root/bin/mezzmover.log'
    pid_file = '/var/run/mezzmover.pid'

    # Number of concurrent processes that will launch
    num_workers = 4

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

    file_queue = multiprocessing.JoinableQueue()
    log_queue = multiprocessing.Queue()

    # Start the logger
    logger = multiprocessing.Process(target=log_it, args=(log_queue, log_file))
    logger.start()

    workers = [FileMover(file_queue, log_queue) for w in xrange(num_workers)]
    for w in workers:
        w.start()

    # Parse the filesystem for files
    provider_list = [p for p in os.listdir(source_dir) if not p.startswith('.')]
    for provider in provider_list:
        provider_path = os.path.join(source_dir, provider)

        p = os.path.join(dest_dir, provider)
        if not os.path.exists(p):
            os.mkdir(p)

        asset_list = [a for a in os.listdir(provider_path) if not a.startswith('.')]
        for asset in asset_list:
            asset_path = os.path.join(provider_path, asset)
            dest_path = os.path.join(dest_dir, provider, asset)
            if os.listdir(asset_path):
                print "Found asset at %s" % asset_path
                file_queue.put((asset_path, dest_path))
            else:
                print "Found empty dir at %s" % asset_path

    for w in xrange(num_workers):
        file_queue.put((None, None))

    file_queue.join()

    log_queue.put(None)
    logger.join()

    # Remove PID 
    os.remove(pid_file)
