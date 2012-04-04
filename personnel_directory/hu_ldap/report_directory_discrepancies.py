"""
Report address, phone, email, and title discrepancies between the MCB directory and Harvard directory

(1) Retrieve all privacy objects
(2) Compare email
(3) Compare phone
(4) Compare addresses
(5) Compare titles

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
from personnel_directory.common.msg_util import msg, msgt
import sys

from personnel_directory.person.models import Person
from mcb.hu_ldap.models import HarvardPersonInfo

DISCREPANCY_TYPE_EMAIL = 'EMAIL'
DISCREPANCY_TYPE_PHONE = 'PHONE'
DISCREPANCY_TYPE_ADDRESS = 'ADDRESS'
DISCREPANCY_TYPE_TITLE = 'TITLE'

class DiscrepancyLineItem:
    def __init__(self, harvard_person_info, discrepancy_type, mcb_vals, uis_vals, msg=''):
        self.harvard_person_info = harvard_person_info
        self.discrepancy_type = discrepancy_type
        self.mcb_vals = mcb_vals
        self.uis_vals = uis_vals
        self.msg = msg
    
    def update_mcb_listing(self):
        """Limited updates to the MCB data based on the UIS data"""
        if self.discrepancy_type == DISCREPANCY_TYPE_PHONE:
            # if there is no MCB number listed, then copy the UIS number to the MCB directory
            if len(self.mcb_vals) == 0 and len(self.uis_vals) == 1:
                self.harvard_person_info.person.phone = self.harvard_person_info.phone
                self.harvard_person_info.person.save()
            return
            
        if self.discrepancy_type == DISCREPANCY_TYPE_EMAIL:
            # if there is no MCB email listed, then copy the UIS email to the MCB directory
            if len(self.mcb_vals) == 0 and len(self.uis_vals) == 1:
                self.harvard_person_info.person.email = self.harvard_person_info.email
                self.harvard_person_info.person.save()
            
            '''
            elif len(self.mcb_vals) == 1 and len(self.uis_vals) == 1:
                # If the MCB directory's 2nd email is blank, and UIS as an @fas email, use it
                if self.harvard_person_info.email.lower().find('@fas.') > -1: 
                    self.harvard_person_info.person.second_email = self.harvard_person_info.email
                    self.harvard_person_info.person.save()
            '''
            
    @staticmethod
    def create_email_discrepancy_item( harvard_person_info):
        mcb_vals = []
        if harvard_person_info.person.email:        
            mcb_vals.append(harvard_person_info.person.email)
        if harvard_person_info.person.second_email:
            mcb_vals.append(harvard_person_info.person.second_email)

        dli = DiscrepancyLineItem(harvard_person_info \
                                , DISCREPANCY_TYPE_EMAIL \
                                , mcb_vals \
                                , [harvard_person_info.email] \
                                , 'UIS email does not match MCB')
        return dli
    
    
    @staticmethod
    def create_phone_discrepancy_item( harvard_person_info):
        mcb_vals = []
        if harvard_person_info.person.phone:        
            mcb_vals.append(harvard_person_info.person.phone)
        if harvard_person_info.person.second_phone:
            mcb_vals.append(harvard_person_info.person.second_phone)

        dli = DiscrepancyLineItem(harvard_person_info \
                                , DISCREPANCY_TYPE_PHONE \
                                , mcb_vals \
                                , [harvard_person_info.phone] \
                                , 'UIS phone number does not match MCB')
        return dli
    
    def show_discrepancy(self, cnt=None):
        #msg('%s - >%s' % (self.harvard_person_info, self.discrepancy_type))
        if cnt:
            msg('-->(%s) %s' % (cnt, self.discrepancy_type))
        else:
            msg('-->%s' % (self.discrepancy_type))
        msg('uis: %s' % ', '.join(self.uis_vals))
        msg('mcb: %s' % ', '.join(self.mcb_vals))
    
    def add_xls_row(self, row_num, spreadsheet_obj):
        pass
        
        
class DirectoryDiscrepancyChecker:

    def __init__(self):

        self.person_lst = HarvardPersonInfo.objects.all()   #filter(lname='Desai')
        self.check_discrepancies()
        
    def check_discrepancies(self):
        """If a discrepancy is found, add a 'discrepancies' attribute to the HarvardPersonInfo object.
        The 'discrepancies' attribute is a [] containing 1 or more DiscrepancyLineItem objects"""
        
        # for each person, check disprepancies
        for hpi in self.person_lst:
            msg(hpi.id)
            msgt('checking person: %s %s' % (hpi.id, hpi) )
            self.check_phone_number(hpi)
            self.check_email_address(hpi)
            self.check_office_address(hpi)  # in progress
            
    def check_phone_number(self, hpi):
        """Check if the UIS phone number matches one of the MCB phone numbers"""
        msg('checking phone number')
        if hpi is None:
            return
        
        conflict_found = False
        #print 'hpi.phone: %s' % hpi.phone
        #print 'hpi.person.phone: %s' % hpi.person.phone
        #print 'hpi.person.second_phone: %s' % hpi.person.second_phone

        if hpi.phone:       
            # the UIS directory has a phone number 
            if hpi.person.phone == hpi.phone or hpi.person.second_phone == hpi.phone:
                pass    # no conflicts
            else:
                # phone numbers don't match
                conflict_found = True
        else:
            # phone number in MCB directory, but not in the main directory
            if hpi.person.phone or hpi.person.second_phone:
                conflict_found = True
        
        # create a DiscrepancyLineItem object and add it to the list of "discrepancies"
        if conflict_found:
            msg('conflict found')
            if not hpi.__dict__.has_key('data_conflicts'):
                hpi.data_conflicts = []
            hpi.data_conflicts.append(DiscrepancyLineItem.create_phone_discrepancy_item(hpi))
      

    def check_email_address(self, hpi):
        """Check if the UIS email address one of the MCB email addresses"""
        msg('checking email address')
        if hpi is None:
            return

        conflict_found = False
        #print 'hpi.phone: %s' % hpi.phone
        #print 'hpi.person.phone: %s' % hpi.person.phone
        #print 'hpi.person.second_phone: %s' % hpi.person.second_phone

        if hpi.email:       
            # the UIS directory has an email address
            if hpi.person.email == hpi.email or hpi.person.second_email == hpi.email:
                pass    # no conflicts
            else:
                # emails don't match
                conflict_found = True
        else:
            # email in MCB directory, but not in the main directory
            if hpi.person.email or hpi.person.second_email:
                conflict_found = True

        # create a DiscrepancyLineItem object and add it to the list of "discrepancies"
        if conflict_found:
            msg('conflict found')
            if not hpi.__dict__.has_key('data_conflicts'):
                hpi.data_conflicts = []
            hpi.data_conflicts.append(DiscrepancyLineItem.create_email_discrepancy_item(hpi))

   
    def check_office_address(self, hpi):
        """Compare the office address of the MCB directory and UIS.  Note, UIS has a different  
        format, concatenated into one string that is delimted by '$'

        UIS address example: RAMAN M PRASAD$Harvard, FAS Molecular & Cell Biology$Northwest Lab Building Rm 190.01$52 Oxford Street$Cambridge MA 02138    
        
        UIS also has separate zipcode and and state fields
         
        """
        msg('checking office address')
        conflict_found = False
        
        print 'hpi.postal_address: %s' % hpi.postal_address
        print 'hpi.person.room: %s' % hpi.person.room
        print 'hpi.person.building: %s' % hpi.person.building

        #if hpi.postal_address:
            
        
    
   
    def show_discrepancies(self):
        
        conflict_found_lst = filter(lambda x: x.__dict__.has_key('data_conflicts'), self.person_lst)
        cnt =0
        for p in conflict_found_lst:
            msgt(p)
            for d in p.data_conflicts:                
                cnt +=1
                d.show_discrepancy(cnt)
                
        print 'people with phone discrepancies: %s' % len(conflict_found_lst)
        
    def send_discrepancy_report(self):
        pass
        
        
        
def send_privacy_report():
    # contruct an email
    msgt('(3) Preparing email with results')
    
    admin_emails = get_admin_email_addresses()
    
    from_email = admin_emails[0]
    to_addresses = admin_emails
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

def show_addr_file():
    outlines = []
    for p in HarvardPersonInfo.objects.all():
        if p.postal_address:
           outlines.append(p.postal_address.replace('$', '\t'))
    fname = 'addr_file.txt'
    open(fname, 'w').write('\n'.join(outlines))
    print 'file written: %s' % fname
    
if __name__=='__main__':
    #show_addr_file()
    ddc = DirectoryDiscrepancyChecker()
    ddc.show_discrepancies()
    #ddc.send_discrepancy_report()
    