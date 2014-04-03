from django.db import models
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField

from django.core.urlresolvers import reverse

from personnel_directory.person.models import Person


class DirectoryNotificationEmail(models.Model):
    email = models.EmailField(help_text='A person who receives notice of missing directory information.', unique=True)
    
    def __unicode__(self):
        return self.email

    class Meta:
        ordering = ('email',)

class HarvardTitle(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
  
class HarvardAffiliation(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)  

class HarvardPersonInfo(models.Model):
    """Used to reconcile information in the MCB and Harvard directories--including privacy flags"""
    person = models.ForeignKey(Person, unique=True)      
    
    uid = models.CharField('ldap uid', max_length=125, blank=True, db_index=True)
    
    # directory info to verify
    lname = models.CharField('Last Name',max_length=255, blank=True)
    fname = models.CharField('First Name', max_length=255, blank=True)
    middle_name = models.CharField('Middle Name', max_length=50, blank=True, default='')      # harvardEduMiddleName

    email = models.EmailField(max_length=255, blank=True)
    phone = PhoneNumberField(blank=True)

    postal_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    zipcode = models.CharField(max_length=14, blank=True)
    state = models.CharField(max_length=10, blank=True)

    titles = models.ManyToManyField(HarvardTitle, null=True, blank=True)
   
    
    eduPersonAffiliation = models.ManyToManyField(HarvardAffiliation, null=True, blank=True)
    
    is_student_role = models.BooleanField(default=False)
    is_employee_role = models.BooleanField(default=False)
    is_poi_role = models.BooleanField('is Person of Interest role', default=False)
    is_library_borrower_role = models.BooleanField(default=False)
    is_xid_holder_role =  models.BooleanField(default=False)
    '''
    alter table hu_ldap_harvardpersoninfo add column `is_xid_holder_role` bool NOT NULL;
    update hu_ldap_harvardpersoninfo set is_xid_holder_role=0;
    '''
    #--------------------------
    # FERPA blocks
    #--------------------------
    harvardEduFerpaPastStudentIndicator = models.BooleanField('FERPA past student', default=False)
    harvardEduFerpaStatus = models.BooleanField('FERPA status', default=False)
    
    #--------------------------
    # full blocks - no directory info
    #--------------------------
    harvardEduStudentPrivacy = models.IntegerField('Student Privacy', default=-1)   # for student role
    harvardEduEmployeePrivacy = models.IntegerField('Employee Privacy', default=-1) # for employee role
    harvardEduSpecialPrivacy = models.IntegerField('Special Privacy',default=-1)    # for role POI (person of interest)

    #--------------------------
    # attribute level blocks - pertains to mcb directory
    #--------------------------
    harvardEduMailPrivacy = models.IntegerField('Mail Privacy',default=-1)  # use for email
    harvardEduOfficeAddressPrivacy = models.IntegerField('OfficeAddress Privacy',default=-1)    # use for office address
    harvardEduPhonePrivacy = models.IntegerField('Phone Privacy',default=-1)    # use for phone number

    # may pertain to grad student listing
    harvardEduImagePrivacy = models.IntegerField('Image Privacy', default=-1)

    harvardEduGender = models.CharField(max_length=10, blank=True, help_text='"M" or "F".  NOT REGULARLY POPULATED - used for a 1-time report')   
    #--------------------------
    # attribute level blocks - not needed for mcb
    #--------------------------    
    harvardEduFaxPrivacy = models.IntegerField('Fax Privacy',default=-1)
    harvardEduHomeAddressPrivacy = models.IntegerField('Home Address Privacy',default=-1)
    harvardEduHomePhonePrivacy = models.IntegerField('Home Phone Privacy',default=-1)
    harvardEduMobilePrivacy = models.IntegerField('Mobile Privacy',default=-1)
    harvardEduDormAddressPrivacy = models.IntegerField('Dorm Address Privacy', default=-1)

    last_update = models.DateTimeField(auto_now=True)
    
    '''
    alter table hu_ldap_harvardpersoninfo add column `last_update` datetime NOT NULL;
    '''
    def __unicode__(self):
        if self.lname and self.fname:
            return '%s, %s' % (self.lname, self.fname)

        return str(self.person)

    class Meta:
        ordering = ('lname', 'fname')
        verbose_name = 'Harvard Personnel Info/Privacy Flags'
        verbose_name_plural = verbose_name



    def has_ferpa_restriction(self):

        # restricted student
        if self.is_student_role and self.harvardEduFerpaStatus:
            return True # restricted
        
        if self.is_employee_role and self.harvardEduFerpaStatus:
            if self.harvardEduFerpaPastStudentIndicator == False:
                return True # restricted
            else:
                # FerpaStatus = Y and FerpaPastStudentIndicator = Y                 
                return False    # not restricted for EE role.   
                
        return False
            

    def is_person_public_at_level(self, level_to_check):
        # look for minimal level at employee/student roles

        # 1st check ferpa
        if self.has_ferpa_restriction():
            return False
            
        # This person has no roles, show them (rare, e.g. out of hu student)
        if self.eduPersonAffiliation.count() == 0:
            return True    

        # role employee, check employee privacy
        if self.is_employee_role and self.harvardEduEmployeePrivacy > -1 and self.harvardEduEmployeePrivacy < level_to_check:
            return False


        # at this check, employee privacy setting over-rides student privacy setting -- this is for a work directory
        if self.is_student_role and self.is_employee_role and self.harvardEduEmployeePrivacy > -1 and self.harvardEduEmployeePrivacy >= level_to_check:
            return True         
            
        # role student, check student privacy
        if self.is_student_role and self.harvardEduStudentPrivacy > -1 and self.harvardEduStudentPrivacy < level_to_check:
            return False

        
        # student or employee that is at or above given
        if self.is_student_role or self.is_employee_role:
            return True
        
        # xidHolders with no role blocks, show them
        if self.is_xid_holder_role:
            if -1 == self.harvardEduStudentPrivacy == self.harvardEduEmployeePrivacy== self.harvardEduSpecialPrivacy:
                return True
        
        # not sure, assume not public
        return False

    def person_link(self):
        """Link to the person admin"""
        if self.person is None or self.person.id is None:
                  return '(no link)'
        change_url = reverse('admin:person_person_change', args=(self.person.id,))
        return '<a href="%s">View Person</a>' % change_url
    person_link.allow_tags = True


    def is_person_level_4_public(self):
        # online, public on harvard computers
        return self.is_person_public_at_level(4)
    is_person_level_4_public.boolean = True

    def is_person_level_5_public(self):
        # online, completely public
        return self.is_person_public_at_level(5)
    is_person_level_5_public.boolean = True


    def save(self):
        if self.has_ferpa_restriction(): # cannot be displayed in internal or external directories
            self.person.visible = False
        else:
            self.person.visible = True
        self.person.save()
            
        super(HarvardPersonInfo, self).save()

'''
from personnel_directory.hu_ldap.models import HarvardPersonInfo
l = HarvardPersonInfo.objects.all()
for p in l: p.save()

'''