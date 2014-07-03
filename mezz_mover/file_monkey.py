#!/usr/bin/env python

import os
import multiprocessing
import shutil
import sys
import time
#from __future__ import division

class FileMonkey(multiprocessing.Process):
    def __init__(self, destination, count, results_queue):
        super(FileMonkey, self).__init__()
        self.results = results_queue
        self.destination = destination
        self.count = int(count)

    def run(self):
        self.worker_dir = os.path.join(self.destination, self.name)
        try:
            os.mkdir(self.worker_dir)
        except OSError:
            print '%s already exists, oh well.' % self.worker_dir
        while True:
            self.burn()
        return

    def burn(self):
        """ Copy the test file to the destination X number of 
        times. Will delete the files. """
        for i in range(count):
            fn = self.name + '-' + str(i) + '.dat'
            dst = os.path.join(self.worker_dir, fn)
            start = time.time()
            with open(dst, 'wb') as f:
                f.write(data)
            end = time.time()
            print dst
            result = (self.name, data_size, end-start)
            self.results.put(result)

#         shutil.rmtree(self.worker_dir)                                                                               

def humanize_bytes(size, precision=2):
    """Return a humanized string representation of a number of bytes."""

    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f %s"%(precision,size,suffixes[suffixIndex])

def print_results(results_queue):
    results = {}
    results['total'] = (0,0)
    for i in range(num_of_monkeys):
        results['Munkey' + str(i)] = (0,0)
    while True:
        if not results_queue.empty():
            output = results_queue.get()
            ps,pt = results[output[0]]
            results[output[0]] = (ps + output[1], pt + output[2])
            #results[output[0]] = (output[1],output[2])
            ps,pt = results['total']
            results['total'] = (ps + output[1], pt + output[2])
            clear()
            print 'Munkey        data written    in  time'
            print '----------------------------------------------'
            for k, v in results.iteritems():
                if k != 'total':
                    print '%s\t\t%s\tin\t%0.2f sec' % (k, humanize_bytes(v[0]), v[1])
            print '----------------------------------------------'
            ts, tt = results['total']
            print 'Total\t\t%s\tin\t%0.2f sec' % (humanize_bytes(ts), tt/num_of_monkeys)

def clear():
    os.system('clear')

if __name__ == "__main__":

    print 'Munkeys away!!!'
    test_file = sys.argv[1]
    data_size = os.path.getsize(test_file)
    with open(test_file, 'rb') as f:
        print 'Reading file into memory, this could take a moment...'
        data = f.read(data_size)
    destination = sys.argv[2]
    num_of_monkeys = multiprocessing.cpu_count()
    count = 10
    results_queue = multiprocessing.Queue()

    rp = multiprocessing.Process(target=print_results, args=(results_queue,))
    rp.start()

    workers = []
    print 'Creating %s Munkies!! ' % num_of_monkeys
    for i in range(num_of_monkeys):
        p = FileMonkey(destination, count, results_queue)
        workers.append(p)
        p.name = "Munkey" + str(i)
        p.start()

    rp.join()
    results_queue.close()
    results_queue.join_thread()

    for w in workers:
        w.join()
