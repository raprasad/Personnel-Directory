"""
Use list of hcom trainees to find their email addresses from the MCB directory

huid -> uis ldap -> get uid -> mcb directory

(input data with huids deleted)
"""
if __name__=='__main__':
    #-------------------------
    # import django settings
    #-------------------------
    import os, sys
    sys.path.append('../../mcb')
    from django.core.management import setup_environ
    import settings
    setup_environ(settings)
else:
    import settings
    
from personnel_directory.common.msg_util import *
import ldap, sys, md5

from helper_classes import MemberInfo
from hu_person_search import HUDirectorySearcher
from personnel_directory.person.models import Person
from mcb.hu_ldap.models import HarvardPersonInfo
from huid_name import huid_map

def map_hcom_to_email():
    searcher = HUDirectorySearcher() 

    cnt =0
    fmt_list = []
    for line in huid_map:
        items = line.split('\t')
        if not len(items) ==2:
            fmt_list.append(line.strip() + '\t?')
        elif len(items)==2:
            cnt+=1
            huid, name = items
            dashes()
            msg('(%s) %s' % (cnt, name))
            lu = {  'huid': huid }
            
            members = searcher.find_people(**lu)
    
            if members is not None:
                member = members[0]
                try:
                    person_info = HarvardPersonInfo.objects.get(uid=member.uid)
                except HarvardPersonInfo.DoesNotExist:
                    print 'person_info not found'
                    person_info = None
            
                if person_info:
                    print person_info.person.email
                    print person_info.person.second_email
                    fmt_list.append('%s\t%s\t%s' % (huid, name, person_info.person.email))
                else:
                    fmt_list.append(line.strip() + '\t?')
            else:
                fmt_list.append(line.strip() + '\t?')
        #if cnt == 10:
        #    break        
    print '\n'.join(fmt_list)  
    open('email_list.txt', 'w').write('\n'.join(fmt_list)  )      
    searcher.close_connection()


if __name__=='__main__':
    map_hcom_to_email()