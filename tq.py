import Queue
import threading
from threading import Thread
import random
import sys
import os
import errno    
import subprocess

# Get SLURM jobid (for directing output)
sjid=os.environ.get('SLURM_JOBID')
if not sjid:
 sjid='NOJOBID'

sd="slurm-%s-out.dir"%sjid
try:
 os.makedirs(sd)
except OSError as exc:
 if exc.errno == errno.EEXIST and os.path.isdir(sd):
  pass
 else:
  raise
od="%s/job%%J.out"%(sd)
ed="%s/job%%J.err"%(sd)

# Get number of slots we have
# cmd='''srun /bin/bash -c 'echo `hostname` ${SLURM_CPUS_ON_NODE}' | sort | uniq | awk 'BEGIN{np=0};{np=np+$2};END{print np}' '''
# p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
# nslots=int((p.communicate())[0])
nslots=4

if nslots:
 num_worker_threads=nslots
else:
 num_worker_threads=4

def do_work(item):
 # srun --output=${odir}/job%J.out --error=${odir}/job%J.err  -N 1 --ntasks=1 --exclusive /bin/bash -c "${cmd}" 
 # cmd="srun -N 1 --ntasks=1 --exclusive"
 # cmd=cmd + " --output=%s "%od
 # cmd=cmd + " --error=%s "%ed
 # cmd=cmd + " /bin/bash -c \"sleep %d ; hostname\""%item['pause']
 cmd="sleep %d"%item['pause']
 print threading.currentThread().getName(), cmd
 p=subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
 print p.communicate()
 return

def source():
 sl=[]
 for x in range(20):
  lp=random.randint(1, 10)
  sl.append({'pause':lp})
 return sl

def worker():
    while True:
        item = q.get()
        try:
         do_work(item)
        except Exception as e:
         print 'Error'
         print e
         pass
        q.task_done()

q = Queue.Queue()
for i in range(num_worker_threads):
     t = Thread(target=worker)
     tn="thread-%d"%i
     t.setName(tn)
     t.daemon = True
     t.start()

for item in source():
    q.put(item)

q.join()       # block until all tasks are done
