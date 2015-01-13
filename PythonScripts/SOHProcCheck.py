#!/usr/bin/python
"""Process to verify that all necessary processes are running
   Should be called as a cron job with /bin/sh -l -c or equivalent
   Pass "nomail" and "debug" as options to turn off mail sending
   and to turn on extra debugging information as needed

"""
import os
import signal
import smtplib
import string, sys
import time
from notify import email

import stat

# Run mode -- set to (0,1) for testing, (1,0) for production

mail = 1
debug = 0 # change this later

# For each process that you want to monitor
# you need a "dictionary" of process name, dictionary command, and "touch" file

timeout = 60 # Timeout for touched files

# For each process that you wish to monitor, set up a
# dictionary object with membership as follows:
#     'procName' : String to search for in a "ps" to verify that the process is running
#     'execute'  : String to run to launch and spawn the process
#     'touchFile': (optional) Process touches this file every so often to
#                  verify that it is still running.

dictTHERfe  ={ 'procName' : 'THERfe',
               'execute'  : '%s/39470A2/THERfe -D' % os.environ['SOHBASEDIR'],
	       'touchFile': '%s/THERfe.counter' % os.environ['HOME']}

dictmhttpd  ={ 'procName' : 'mhttpd',
               'execute'  : '%s/linux/bin/mhttpd -p 8081 -D' % os.environ['MIDASSYS']}

dictmlogger ={ 'procName' : 'mlogger',
               'execute'  : '%s/linux/bin/mlogger -D' % os.environ['MIDASSYS']}

dictEPICSfe ={ 'procName' : 'fe_epics',
               'execute'  : '%s/epics/startEPICSfe' % os.environ['SOHBASEDIR'] }

listofprocs =[ dictmhttpd, dictmlogger, dictTHERfe , dictEPICSfe ]	       

#Subroutines within proc-check
	       
def seekProcs(PROCESSNAME):
    """Search for OS processes with this name
       and return process numbers as a list """
    procstokill = []
    pscmd = "ps -C " + PROCESSNAME
    for line in os.popen(pscmd):
        fields = line.split()
        pid = fields[0]
        process = fields[3]      
        last = fields[-1]
        if process == PROCESSNAME and last != '<defunct>':
            procstokill.append(pid)
    return procstokill
      
def killProcs(list):
    """ Kill processes with numbers in list """
    for pid in list:
        os.system("kill -9 %s" % pid)

#start of main processing

SUBJ = "" # no subject to start subject
BODY = "" # No body yet. If there is anything to notify about, do it later 

# Get cmd line options if any
for arg in sys.argv:
  print arg
  if (arg=='nomail'):
    mail=0
    print "Mail will be suppressed \n"
  elif (arg=='debug'):
    debug = 1
    print "Debugging stuff will be printed \n"

# Check for environ variably MIDASSYS and set it to a default if needed
# This little bit of code was needed before it was determined that cron
# wouldn't pass all the necessary environment variables on its own and
# that you had to run it as /bin/sh -l -c SOHProcCheck.py in order for
# it to work properly.

if 'MIDASSYS' in os.environ:
  if (debug):
    print 'MIDASSYS environment variable found and equals ',
else:
  os.environ['MIDASSYS']='/opt/midas'
  if (debug):
    print 'MIDASSYS not found in environment:  forced to ',
if (debug):
  print (os.environ['MIDASSYS'])

if 'MIDAS_EXPT_NAME' in os.environ:
    if (debug):
        print 'MIDAS_EXPT_NAME variable found and equals ',
else:
    os.environ['MIDAS_EXPT_NAME']='tigsohdev'
    if (debug):
        print 'MIDAS_EXPT_NAME not found in environment:  forced to ',
if (debug):
    print (os.environ['MIDAS_EXPT_NAME'])

if 'MIDAS_EXPTAB' in os.environ:
    if (debug):
        print 'MIDAS_EXPTAB variable found and equals ',
else:
    os.environ['MIDAS_EXPTAB']='%s/Experiments/exptab' % os.environ['HOME']
    if (debug):
        print 'MIDAS_EXPTAB not found in environment:  forced to ',
if (debug):
    print (os.environ['MIDAS_EXPTAB'])

for procDict in listofprocs:
    deltaTime = 0 # time since Touchifle was last touched

    procName = procDict['procName']
    execute =  procDict['execute']
    
    listofPIDs = seekProcs(procName)
    # Get time since last "touch", if needed
    if 'touchFile' in procDict:
        if (os.path.isfile(procDict['touchFile']) == False):
            SUBJ += procName
            BODY += procName + " touch file does not exist\n"
        else:
            deltaTime = int(time.time())-os.stat(procDict['touchFile'])[stat.ST_MTIME] 
    if (debug):
       print procName + " " + `listofPIDs` + " " + `deltaTime`
    # If everything's normal, then the file will have been touched and the PID list will have 1 #
    if ( (deltaTime<timeout) and (len(listofPIDs)==1) ):
        continue # so move on to the next process
    # Something's not normal here
    SUBJ += procName
    BODY += procName + ": process list " + `listofPIDs` + "\n"
    if deltaTime > 0:
        BODY += "          file untouched %s seconds \n" % deltaTime
    killProcs(listofPIDs) # kill -9 any outstanding processes
    os.system('%s/linux/bin/odbedit -c cleanup' % os.environ['MIDASSYS']) # Cleanup
    BODY += "          Restart with command " + execute + "\n"
    os.system(execute)
    listofPIDS = seekProcs(procName)
    BODY += "          Restarted as process " + `listofPIDS` + "\n"
    if (len(listofPIDS)!=1):
        BODY += "      ** THIS IS AN URGENT PROBLEM. FIX IT **\n"
        SUBJ += " WARNING"
       
# Back to main level
# At this point you should have one of each process running
# If Subject is NOT empty, send an e-mail
if (len(SUBJ) != 0):
    SUBJ = "grifsoh process notification: "+SUBJ
    BODY = BODY + "generated by "+ os.path.abspath(__file__)  
    if mail:
        email(SUBJ,BODY)

if debug:
    print "Subject: " + SUBJ+"\n"
    print """Message body:
""" + BODY
    

# end
