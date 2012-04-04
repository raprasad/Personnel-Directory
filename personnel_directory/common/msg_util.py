import os, sys, string
from django.conf import settings


def msg(s):
    if settings.DEBUG:
        print s
    
def dashes():
    msg(40*'-')

def msgt(s):
    dashes()
    msg(s)
    dashes()

def msgu(s):
    dashes()
    msg(s)
    
def msgx(s):
    msgt('Error')
    msg(s)
    dashes()
    sys.exit(0)
    
def strip_list_of_strings(lst):
    lst = map(string.strip, lst)
    return filter(lambda x: len(x) > 0, lst)
    
def write_to_file(fname, content):
    open(fname,'w').write(content)
    msgt('file written: %s' % fname)

def get_fcontent(fname):
    try:
        return open(fname,'r').read()
    except IOError:
        msgx('could not read file: %s' % fname)

def fmt_time_desc(hours=0, minutes=0):
    hh = ''
    if hours >= 1:
        if hours == 1:
            hh = '%s hour'% hours
        else:
            hh = '%s hours'% hours
    
    mm = ''
    if minutes >=1:
        if minutes == 1:
            mm = '%s minute' % minutes
        else:
            mm = '%s minutes' % minutes
        if hours < 1:
            return mm
    else:               
        return hh
    
    return '%s, %s' % (hh, mm)
        
        
if __name__=='__main__':
    lst = ['afadsf', 'err  ', '  df33']
    lst = strip_list_of_strings(lst)
    print lst