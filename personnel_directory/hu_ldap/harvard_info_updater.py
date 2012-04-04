"""
Working on the hu ldap / personnel db connection

crontab entry:

# update individual privacy settings every tues morning at 8:35 am
# 35 8 * * 2 /usr/bin/python /usr/local/django-apps/mcb/mcb/hu_ldap/harvard_info_updater.py
50 9 * * 2 /usr/bin/python /usr/local/django-apps/mcb/mcb/hu_ldap/harvard_info_updater.py
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

from personnel_directory.common.time_util import get_datetime_now
from personnel_directory.common.mailer import send_message, get_admin_email_addresses

from personnel_directory.common.msg_util import *

from personnel_directory.person.models import Person
from mcb.hu_ldap.models import HarvardPersonInfo, HarvardTitle, HarvardAffiliation
from hu_person_search import HUDirectorySearcher

class HarvardPersonInfoUpdater:
    
    def __init__(self):
        self.searcher = HUDirectorySearcher()
        self.msg_lines = []
        self.num_records_updated = 0

    def close_searcher_connection(self):
        if self.searcher:
            self.searcher.close_connection()
    
    def add_msg_line(self, l):
        if l is None:
            return
        self.msg_lines.append(l)
        
    def update_existing_harvard_info_objects(self):
        """Reconcile directory with HU LDAP"""
        msgt('update existing harvard info objects')
        
        cnt =0
        for hp in HarvardPersonInfo.objects.all():
            self.update_person_info(hp, cnt)
            cnt+=1
            self.num_records_updated+=1
            #if cnt==25: break
                
        self.close_searcher_connection()
            
    def update_person_info(self, hu_info_obj, cnt=0):
        if hu_info_obj is None:
            return
        #msg('(%s) updating %s' % (cnt, hu_info_obj))
        members = self.searcher.find_people(uid=hu_info_obj.uid)    

        if members is None:
            note = '''> Not found.  HarvardPersonInfo with id [%s][%s]
- https://webapps.sciences.fas.harvard.edu/mcb/mcb-control-panel/hu_ldap/harvardpersoninfo/%s/''' % (hu_info_obj.id, hu_info_obj, hu_info_obj.id)
            self.add_msg_line(note)
            msg(note)
            
        elif len(members)==1:
            m = members[0]
            cnt+=1
            dashes()
            msg('(%s) %s %s' % (cnt, m.givenName, m.sn))
            #m.show()
            hu_info_obj.lname = m.get_or_blank('sn')
            hu_info_obj.fname = m.get_or_blank('givenName')
            hu_info_obj.email = m.get_or_blank('mail')
            hu_info_obj.middle_name = m.get_or_blank('harvardEduMiddleName')

            if m.telephoneNumber is not None:
                phone_num_parts = m.telephoneNumber.split()
                if len(phone_num_parts) == 4:
                    hu_info_obj.phone = '-'.join(phone_num_parts[1:])

            hu_info_obj.city = m.get_or_blank('l')
            hu_info_obj.state = m.get_or_blank('st')
            hu_info_obj.zipcode = m.get_or_blank('postalCode')
            hu_info_obj.postal_address = m.get_or_blank('postalAddress')
            
       
            # ferpa
            if m.harvardEduFerpaStatus == 'TRUE':
                hu_info_obj.harvardEduFerpaStatus = True
            else:
                hu_info_obj.harvardEduFerpaStatus = False

            if m.harvardEduFerpaPastStudentIndicator == 'TRUE':
                hu_info_obj.harvardEduFerpaPastStudentIndicator = True
            else:
                hu_info_obj.harvardEduFerpaPastStudentIndicator = False
                
            #print 'get or neg 1', m.get_or_neg1('harvardEduImagePrivacy')
            # additional privacy
            hu_info_obj.harvardEduImagePrivacy = m.get_or_neg1('harvardEduImagePrivacy')
            hu_info_obj.harvardEduSpecialPrivacy = m.get_or_neg1('harvardEduSpecialPrivacy')
            hu_info_obj.harvardEduEmployeePrivacy = m.get_or_neg1('harvardEduEmployeePrivacy')
            hu_info_obj.harvardEduStudentPrivacy = m.get_or_neg1('harvardEduStudentPrivacy')
            hu_info_obj.harvardEduMailPrivacy = m.get_or_neg1('harvardEduMailPrivacy')
            hu_info_obj.harvardEduPhonePrivacy = m.get_or_neg1('harvardEduPhonePrivacy')
            hu_info_obj.harvardEduFaxPrivacy = m.get_or_neg1('harvardEduFaxPrivacy')
            hu_info_obj.harvardEduHomePhonePrivacy = m.get_or_neg1('harvardEduHomePhonePrivacy')
            hu_info_obj.harvardEduMobilePrivacy = m.get_or_neg1('harvardEduMobilePrivacy')
            hu_info_obj.harvardEduOfficeAddressPrivacy = m.get_or_neg1('harvardEduOfficeAddressPrivacy')
            hu_info_obj.harvardEduHomeAddressPrivacy = m.get_or_neg1('harvardEduHomeAddressPrivacy')
            hu_info_obj.harvardEduDormAddressPrivacy = m.get_or_neg1('harvardEduDormAddressPrivacy')
       	
            hu_info_obj.save()
        	
        	# reset titles
            hu_info_obj.titles.clear()
            if not m.title is None:
                for t in m.title:
                    try:
                        tobj = HarvardTitle.objects.get(name=t)
                    except HarvardTitle.DoesNotExist:
                        tobj = HarvardTitle(name=t)
                        tobj.save()
                    hu_info_obj.titles.add(tobj)
            hu_info_obj.save()
            
            
            hu_info_obj.is_student_role = False
            hu_info_obj.is_employee_role = False
            hu_info_obj.is_poi_role = False
            hu_info_obj.is_library_borrower_role = False
            
            # reset roles
            hu_info_obj.eduPersonAffiliation.clear()
            if not m.eduPersonAffiliation is None:
                for role in m.eduPersonAffiliation:
                    if role is not None and not role.strip() == '':
                        if role == 'employee': hu_info_obj.is_employee_role = True
                        if role == 'student': hu_info_obj.is_student_role = True
                        if role == 'xidHolder': hu_info_obj.is_xid_holder_role = True
                        
                        try:
                            tobj = HarvardAffiliation.objects.get(name=role)
                        except HarvardAffiliation.DoesNotExist:
                            tobj = HarvardAffiliation(name=role)
                            tobj.save()
                        hu_info_obj.eduPersonAffiliation.add(tobj)
            hu_info_obj.save()

            #eduPersonAffiliation = models.ManyToManyField(HarvardAffiliation, null=True, blank=True)
            '''
            is_student_role = models.BooleanField(default=False)
            is_employee_role = models.BooleanField(default=False)
            is_poi_role = models.BooleanField('is Person of Interest role', default=False)
            is_library_borrower_role = models.BooleanField(default=False)
            '''
            
                        
        else:
            note = '''> More than one entry found.  HarvardPersonInfo with id [%s][%s]
- https://webapps.sciences.fas.harvard.edu/mcb/mcb-control-panel/hu_ldap/harvardpersoninfo/%s/''' % (hu_info_obj.id, hu_info_obj, hu_info_obj.id)
            self.add_msg_line(note)
            msg(note)
        
        
    
    def send_update_report(self):

        msgt('Preparing email with report')
        admin_emails = get_admin_email_addresses()    
        # add susan, kim, and natacha to email notice
        for additional_email in 'sfoster@mcb.harvard.edu coady@fas.harvard.edu nesterlin@mcb.harvard.edu'.split():
            admin_emails.append(additional_email)
        
        from_email = admin_emails[0]
        to_addresses = admin_emails
        
        if len(self.msg_lines) == 0:
            subject = 'Privacy Data Updates: Looks Good! %s records checked' % self.num_records_updated 
            mail_msg = """Existing privacy records updated.\n\n%s records checked.  No errors.\n\n(%s)""" % (self.num_records_updated,get_datetime_now())
        else:
            subject = 'Privacy Data Updates: %s error notes' % len(self.msg_lines)
            mail_msg = """%s records checked. The following records had error messages: 

    %s

    (time %s)""" % (self.num_records_updated, '\n\n'.join(self.msg_lines),   get_datetime_now() )

        mail_msg += """
        
Note: This is a weekly check to ensure that people in the MCB directory are still in the HU's central directory.  
        
The possible reasons for a person failing the check are:
        
(1) The person has left the University
(2) The last name of the person has changed
"""

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
    updater = HarvardPersonInfoUpdater()
    updater.update_existing_harvard_info_objects()
    updater.send_update_report()