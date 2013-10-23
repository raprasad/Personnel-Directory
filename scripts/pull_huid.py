import os, sys

def msg(s): print s
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()

sys.path.append('/var/webapps/django/MCB-Website')
sys.path.append('/var/webapps/django/MCB-Website/mcb_website')

from mcb_website import settings
from django.core.management import setup_environ
setup_environ(settings)

from personnel_directory.hu_ldap.hu_person_search import HUDirectorySearcher

from hu_ldap.models import *

class HUIDRetriever:

    def __init__(self, output_fname=None):
        self.output_fname = output_fname
        self.huid_list = []
        self.huid_key_list = []
        self.huid_lu = {}
        self.load_huids()
        
    def load_huids(self):
        msgt('Loading HUIDs')
        hu_info_objects = HarvardPersonInfo.objects.all()
        
        msg('Checking %s record(s)' % hu_info_objects.count())
        
        searcher = HUDirectorySearcher() 
        cnt=0
        for hu_info in hu_info_objects:
            cnt+=1
            msgt('(%s) %s [%s]' % (cnt, hu_info, hu_info.uid))
            kw_lu = { 'uid' : hu_info.uid }
            members = searcher.find_people(**kw_lu)
            if members is not None:
                minfo = members[0]
                print minfo.harvardEduIDNumber
                self.huid_lu.update({ hu_info.uid : minfo.harvardEduIDNumber })
                self.huid_key_list.append('%s|%s|%s' % (hu_info.id\
                                            , minfo.harvardEduIDNumber\
                                            , minfo ))
            if cnt == 10: break
        searcher.close_connection()        
        self.huid_list = self.huid_lu.values()
        self.huid_list.sort()
        self.huid_list = filter(lambda x: len(x.strip()) > 0, self.huid_list)
        msg('HUIDs found: %s' % len(self.huid_list))
        if self.output_fname:
            open(self.output_fname, 'w').write('\n'.join(self.huid_list))
            print 'huids written to file: %s' % self.output_fname
            
            keylist_fname = 'keylist-%s' % self.output_fname
            open(keylist_fname, 'w').write('\n'.join(self.huid_key_list))
            print 'huid keys written to file: %s' % keylist_fname
            
if __name__=='__main__':
    HUIDRetriever('huids_2013_1023.txt')


