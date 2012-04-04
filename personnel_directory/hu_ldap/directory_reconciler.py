"""
Working on the hu ldap / personnel db connection
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

from personnel_directory.common.msg_util import *
from personnel_directory.person.models import Person
from personnel_directory.hu_ldap.models import HarvardPersonInfo
from hu_person_search import HUDirectorySearcher
from mcb.hu_ldap.harvard_info_updater import HarvardPersonInfoUpdater

'''
(1) Look up all Person objects
(2) Connect them to the HarvardPersonInfo objects, when possible
(3) Check people w/o HarvardPersonInfo objects
(4) Verify that HarvardPersonInfo still valid
(5) Compare phone, email, titles, and addresses

# list of people w/o privacy info
from person.models import *
lst = Person.objects.filter(visible=True)
no_info = filter(lambda x: x.harvardpersoninfo_set.count()==0, lst)


'''
class DirectoryReconciler:
    def __init__(self):
        
        self.people = None
        self.people_without_harvard_info = None
        self.people_with_address_discrepancies= None
        
        self.load_people()  # initialize self.people and self.people_without_harvard_info
        
        self.hu_ldap_searcher = HUDirectorySearcher()
        self.connect_people_without_harvard_info()
        self.hu_ldap_searcher.close_connection()
        
    def connect_people_without_harvard_info(self):
        if self.people_without_harvard_info is None:
            return
        
        info_updater = HarvardPersonInfoUpdater()
        #msgt('')
        for p in self.people_without_harvard_info:
            reconcile(self.hu_ldap_searcher, p, info_updater)

        info_updater.close_searcher_connection()
        
    def compare_contact_info(self):
        if self.people is None:
            return
        
        msgt('phone differences')
        phone_mismatch_cnt =0
        for p in self.people:
            if p.hu_info is not None and p.hu_info.phone is not None:
                if p.phone == p.hu_info.phone or p.second_phone == p.hu_info.phone:
                    pass
                else:
                    try:
                        phone_mismatch_cnt += 1                    
                        print '\n(%s) %s *%s* - \nhu:[%s] \nmcb:[%s | %s]' % (phone_mismatch_cnt, p, p.appointment, p.hu_info.phone, p.phone, p.second_phone)
                    except UnicodeDecodeError:
                        pass

        email_mismatch_cnt =0
        msgt('email differences')
        for p in self.people:
            if p.hu_info is not None and p.hu_info.email is not None:
                if p.hu_info.email in [p.email, p.second_email, p.ad_username, p.fas_username]:
                    pass
                else:
                    try:
                        email_mismatch_cnt += 1                    
                        print '\n(%s) %s *%s* - \nhu:[%s] \nmcb:[%s | %s | %s | %s]' % (email_mismatch_cnt, p, p.appointment, p.hu_info.email, p.email, p.second_email, p.ad_username, p.fas_username)
                    except UnicodeDecodeError:
                        pass

            
                

    def show_stats(self):
        if self.people_without_harvard_info is None:
            return
            
        cnt=0
        msgt('people without harvard info')
        for p in self.people_without_harvard_info:
            cnt +=1
            print cnt, p
        
    def load_people(self):
        
        # retrieve all people in directory
        people = Person.objects.all()
        
        # retrieve HarvardPersonInfo objects
        pinfo_lst = HarvardPersonInfo.objects.filter(person__id__in=people.values_list('id', flat=True))

        # put the HarvardPersonInfo ojbects into a lookup
        pinfo_dict = dict([(obj.person_id, obj) for obj in pinfo_lst])

        # attached info to people
        for person in people:
            person.hu_info = pinfo_dict.get(person.id, None)
        
        self.people = people
        self.people_without_harvard_info = filter(lambda x: x.hu_info is None, people)
    
    
def reconcile(searcher, person, info_updater):
    """Reconcile directory with HU LDAP"""

    msgt('reconcile: %s (%s)' % ( person, person.id))
    
    lname = person.lname.replace('(', '').replace(')', '')
    fname = person.fname.replace('(', '').replace(')', '')
           
    # 1st pass, match on email
    if person.fas_username:
        members = searcher.find_people(email=person.fas_username)                        
    else:
        members = searcher.find_people(email=person.email)        

    if members is None:
        # 2nd pass, mcb_username
        if person.ad_username:
            members = searcher.find_people(email=person.ad_username)        
            
        # 3rd pass, match on fname, lname            
        if members is None:
            members = searcher.find_people(lname=lname, fname=fname)        
            
    if members is None:
        print ':( not found'        
    elif len(members) == 1:
        m = members[0]
        if m.uid is not None:
            hu_info = HarvardPersonInfo(uid=m.uid, person=person)
            hu_info.save()
            info_updater.update_person_info(hu_info)            
            person.hu_info = hu_info
            
        # make HarvardPersonInfo object
        print 'FOUND!'
    elif len(members) > 1:
        print 'too many found'  


           
if __name__=='__main__':
    dr = DirectoryReconciler()
    dr.compare_contact_info()
    #show_stats()
    #reconcile()