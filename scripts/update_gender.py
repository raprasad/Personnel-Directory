import os, sys

def msg(s): print s
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()
def msgx(s): dashes(); msg(s); dashes(); sys.exit(0)

sys.path.append('/Users/rprasad/mcb-git/MCB-Website')
sys.path.append('/Users/rprasad/mcb-git/MCB-Website/mcb_website')
sys.path.append('/var/webapps/django/MCB-Website')
sys.path.append('/var/webapps/django/MCB-Website/mcb_website')

from mcb_website import settings
from django.core.management import setup_environ
setup_environ(settings)

from personnel_directory.hu_ldap.models import HarvardPersonInfo

from hu_ldap.models import *

class GenderUpdate:
    def __init__(self, huid_gender_file, huid_key_file):
        self.huid_gender_file = huid_gender_file   # 13456789|M
        self.huid_key_file = huid_key_file      # 134|13456789|some name
        
        self.huid_gender_dict = {}
        
        self.make_updates()

    def make_updates(self):
        self.load_huid_gender_lookup()
        self.process_huid_key_file()
    
    def process_huid_key_file(self):
        
        flines = open(self.huid_key_file, 'r').readlines()
        flines = map(lambda x: x.strip(), flines)
        for idx, line in enumerate(flines): 
            db_id, huid, name = line.split('|')
            gender= self.huid_gender_dict.get(huid, None)
            if gender is None:
                continue
                
            try:
                person_info = HarvardPersonInfo.objects.get(pk=db_id)
            except HarvardPersonInfo.DoesNotExist:
                msgx('(%s) Person not found for id: %s (name: %s)' % (idx, db_id, name))
            
            person_info.harvardEduGender = gender
            person_info.save()
            msg('(%s) gender updated: [%s] [%s]' %  (idx, gender, name))
                
  
    def load_huid_gender_lookup(self):
        msgt('load_huid_gender_lookup')
        if not os.path.isfile(self.huid_gender_file):
            msgx('fine not found: %s' % self.huid_gender_file)

        flines = open(self.huid_gender_file, 'r').readlines()
        flines = map(lambda x: x.strip(), flines)
        
        for idx, line in enumerate(flines): 
            if idx == 0: continue   # skip first line
            huid, gender = line.split('|')
            self.huid_gender_dict.setdefault(huid, gender)


if __name__=='__main__':
    GenderUpdate(huid_gender_file='huid_gender.txt'\
                , huid_key_file='keylist-huids_2013_1023.txt')


