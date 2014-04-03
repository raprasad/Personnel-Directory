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

def send_privacy_report():
    # retrieve person objects
    msgt('(1) retrieving Person objects')
    lst = Person.objects.filter(visible=True)
    msg('number found: %s' % lst.count())
    
    # filter out objects without privacy information
    msgt('(2) Filtering people without privacy info')    
    no_info = filter(lambda x: x.harvardpersoninfo_set.count()==0, lst)
    msg('people w/o privacy info: %s' % len(no_info))

    # contruct an email
    msgt('(3) Preparing email with results')
    
    admin_emails = get_admin_email_addresses()    
    from_email = admin_emails[0]
    to_addresses = admin_emails
    
    for email in DirectoryNotificationEmail.objects.all():
        admin_emails.append(email)
    
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

if __name__=='__main__':
    send_privacy_report()
