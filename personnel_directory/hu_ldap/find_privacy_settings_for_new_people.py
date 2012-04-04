"""
Simple script to show people in the directory who lack privacy settings

new crontab under "/home/rprasad"

# check for people w/o privacy settings every tues morning at 8:30 am
30 8 * * 2 /usr/bin/python /usr/local/django-apps/mcb/mcb/hu_ldap/find_people_without_privacy_settings.py


"""
if __name__=='__main__':
    #-------------------------
    # import django settings
    #-------------------------
    import os, sys
    sys.path.append('../../mcb')
    prod_path = '/usr/local/django-apps/mcb/mcb'
    if os.path.isdir(prod_path):
        sys.path.append(prod_path)

    from django.core.management import setup_environ
    import settings
    setup_environ(settings)
else:
    import settings
    
from personnel_directory.common.time_util import get_datetime_now
from personnel_directory.common.mailer import send_message, get_admin_email_addresses
import sys


from mcb.hu_ldap.hu_person_search import HUDirectorySearcher
from mcb.hu_ldap.harvard_info_updater import HarvardPersonInfoUpdater
from personnel_directory.hu_ldap.models import HarvardPersonInfo
from personnel_directory.person.models import Person

def msg(s):
    try:
        print s
    except:
        pass
        
def dashes():
    msg(40*'-')

def msgt(s):
    dashes()
    msg(s)
    dashes()



def create_harvard_person_info_object(person, hu_ldap_info):
    """Create HarvardPersonInfo record
    - start 'minimal' object with person and uid attributes
    - update the object using the HU LDAP connection
    """
    msg('creating HarvardPersonInfo object for: %s' % person)
    hu_person = HarvardPersonInfo(person=person
                            , uid=hu_ldap_info.uid)
    hu_person.save()
    msg('basic object created: %s' % hu_ldap_info.uid)
    updater = HarvardPersonInfoUpdater()
    updater.update_person_info(hu_person)
    updater.close_searcher_connection()
    msg('object updated!')
    
def find_hu_info(directory_searcher, person):
    """Given an mcb.models.Person, create a HarvardPersonInfo record
        Try options in the following order:
            (1) email match
            (2) first name and last name
            X(3) last name
    """
    if person is None:
        return
    
    msg('> Searching HU LDAP for: %s' % person)
    
    msg('> 1st pass - email: %s' % person.email)
    members = directory_searcher.find_people(**{ 'email':person.email })
    if members is None or len(members)==0:
        msg('Fail: no one found by that email')
    elif len(members)==1:
        msg('ldap record found!')
        create_harvard_person_info_object(person, members[0])
        return
    elif len(members) > 2:
        msg('Too many people, try to filter by email and last name')
        members = directory_searcher.find_people(**{ 'email':person.email,\
                                                'lname':person.lname })
        if members is not None and len(members)==1:
            msg('ldap record found!')
            create_harvard_person_info_object(person, members[0])
            return
        elif len(members)==0:
            msg('fail with email and last name filter. NO hits')
        elif len(members) > 0:
            msg('fail with email and last name filter. still TOO MANY hits')

    
    msg('> 2nd pass - lname, fname: %s' % person)
    members = directory_searcher.find_people(**{ 'fname':person.fname,\
                                            'lname':person.lname })

    if members is not None and len(members)==1:
        msg('ldap record found!')
        create_harvard_person_info_object(person, members[0])
        return
    elif members is None or len(members)==0:
        msg('Fail: no one found by that name')
    elif len(members) > 0:
        msg('Fail: TOO MANY records found: %s'  % len(members))
        
    

def get_people_without_harvard_info():
    """
    Get people without privacy settings
    """
    # retrieve person objects
    msgt('(1) retrieving Person objects')
    lst = Person.objects.filter(visible=True)
    msg('number found: %s' % lst.count())
    
    # filter out objects without privacy information
    msgt('(2) Filtering people without privacy info')    
    no_info = filter(lambda x: x.harvardpersoninfo_set.count()==0, lst)
    msg('people w/o privacy info: %s' % len(no_info))

    return no_info

    # contruct an email
    msgt('(3) Preparing email with results')
    
    admin_emails = get_admin_email_addresses()    
    from_email = admin_emails[0]
    to_addresses = admin_emails
    #from_email = 'raman_prasad@harvard.edu'
    #to_addresses = ['raman_prasad@harvard.edu', 'prasad@fas.harvard.edu',]
    if len(no_info) == 0:
        subject = 'Personnel Privacy Data: Looks Good!' 
        mail_msg = """Every person has a privacy record. (%s)""" % get_datetime_now()
    else:
        subject = 'Personnel Privacy Data: %s people do not have info' % len(no_info)
        
        person_lst = '\n\n'.join(map(lambda x: '- %s - %s'  % (x, \
'https://webapps.sciences.fas.harvard.edu/mcb/mcb-control-panel/person/person/%s/' % x.id), no_info ))
        
        mail_msg = """The following people lack privacy records: 
        
%s

(time %s)""" % (person_lst,   get_datetime_now() )
    
    msg('from: %s' % from_email)
    msg('to_addresses: %s' % to_addresses)
    msg('mail_msg: %s' % mail_msg)

    msgt('(4) Sending email with results')
    
    send_message(from_email,\
                to_addresses, \
                subject=subject,\
                text_content=mail_msg,\
                html_content=mail_msg.replace('\n', '<br />'))
        
    msg('Email sent!')
    msgt('Done')



def make_privacy_updates():
    people_without_privacy_recs = get_people_without_harvard_info()
    cnt=0
    directory_searcher = HUDirectorySearcher() 
    
    for p in people_without_privacy_recs:
        msgt('Attempt to add privacy record for: %s' % p)
        cnt+=1
        find_hu_info(directory_searcher, p)
    directory_searcher.close_connection()
    

if __name__=='__main__':
    make_privacy_updates()
