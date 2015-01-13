#!/usr/local/bin/python

import os
import smtplib
import string, sys
import notify


#
# noftify.email(subject,body):  Send e-mails w/ subject & body
# This allows for some "standard" info to be put in
# like e-mail recipients
# or who generated the e-mail

def email(SUBJ,BODY,TO=None,FROM="grifsoh@triumf.ca"):
  """ noftify.email(subject,body):  Send e-mails w/ subject & body
This allows for some standard info to be put in like e-mail recipients
 or who generated the e-mail"""
  HOST = "localhost"
  server = smtplib.SMTP(HOST)
  if TO==None:
    FILE = open('%s/PythonScripts/email.txt' % os.environ['SOHBASEDIR'])
    TT = FILE.readlines()
    TO = []
    for toline in TT:
      TO.append(toline.strip())
    TOS = string.join(TO,",")
  body = string.join((
    "From: %s" % FROM,
    "To: %s" % TOS,
    "Subject: %s" % SUBJ,
    "",
    BODY), "\r\n")
  server.sendmail(FROM, TO, body)
  server.quit()
# end of email


def processfind(NAME, PATH):
  """This function will output the number of times the process designated by name
  is running.  If the process is not found, it starts the process. If the process has one
  occurrence, this function does nothing. If the process has multiple occurences, it kills all processes and starts the process as a daemon."""
  def seekit(PROCESSNAME):
    found = 0
    procstokill = []
    pscmd = "ps -C" + PROCESSNAME
    for line in os.popen(pscmd):
#      print line
      fields = line.split()
      pid = fields[0]
      process = fields[3]
#      print "       pid="+pid+" process="+process
      if process == PROCESSNAME:
    	found += 1
        procstokill.append(pid)
    return procstokill
  
  procstokill = seekit(NAME)

  if (len(procstokill)==1):
    return 1
  body = "Process %s on tigsoh unexpected status:\n" % NAME # Body of an e-mail that might have to be sent
  body +=  "Initially found %s instances of %s\n" % (len(procstokill),NAME)
  if len(procstokill) > 1:
    for pid in procstokill:
      body += "   Killing pid %s\n" % pid
      os.system("kill -9 %s" % pid)
    procstokill = seekit(NAME)
    body += "After kill attempts, found %s instances of %s\n" % (len(procstokill),NAME)
    if len(procstokill) != 0:
      body += "There should have been no instances.\nThis cannot be fixed automatically and requires immediate expert attention."
      subject = "CRITICAL: tigsoh: problem with process %s" % NAME
      email(SUBJ,BODY)
      return len(procstokill)
  body += "Starting %s by os.system(%s)\n" % (NAME,PATH)
  body += "Please notify an expert if this occurs more than once per hour."
  subject = "Notice: tigsoh: restarting process %s" % NAME
  os.system(PATH)
  return len(procstokill)

