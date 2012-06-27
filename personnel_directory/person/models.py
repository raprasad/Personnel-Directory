import os
import Image
from django.conf import settings

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import force_unicode 
from django.db.models.signals import post_save      

from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from building.models import Building
from django.template.loader import render_to_string

import hashlib

MCB_AFFILIATION_ID = 1
APPOINTMENT_TYPE_ID_MCB_GRADUATE_STUDENT = 30

PERSON_PROFILE_IMAGE_SIZE = 150
PERSON_PROFILE_THUMB_IMAGE_SIZE = 100

THUMB_UPLOAD_TO = os.path.join('person', 'thumb')
PROFILE_UPLOAD_TO = os.path.join('person', 'profile')

class PersonAffiliation(models.Model):
    """Default is MCB -- if no appointment clear, indicate home institution / department"""
    name = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class PersonnelCategory(models.Model):
    """Annual Academic 
    Faculty    
    Staff
    Student
    Research"""
    
    name = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Personnel Categories'

class AppointmentType(models.Model):
    """
    Associate   
    Courtesy 

    Faculty
    Faculty (affiliate)
    Postdoctoral Fellow
    Fellows

    Graduate Student    - MCB
    Graduate Student (non-MCB)  - non-MCB graduate student
    Undergraduate Student

    Lecturer
    Preceptor

    Research Associate  - Annual Academic
    Visiting Scholar

    Staff
    LHT
    Temporary   - staff with 3 months appointment
    """
    
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=150, blank=True)
    personnel_category = models.ForeignKey(PersonnelCategory, on_delete=models.PROTECT)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class Lab(models.Model):
    name = models.CharField(max_length=255, unique=True)
    url = models.SlugField('slug', blank=True)
    affiliation = models.ForeignKey(PersonAffiliation, on_delete=models.PROTECT)
    name_affil = models.CharField(max_length=255, blank=True, help_text='auto-filled on save')
    
    def save(self):
        if self.affiliation.id == MCB_AFFILIATION_ID:    # affiliation is mcb
            self.name_affil = self.name            
        else:
            self.name_affil = self.__unicode__()            
        
        self.url = slugify(self.name)
        
        
        super(Lab, self).save()        # Call the "real" save() method.

    def get_absolute_url(self):
        return 'http://www.mcb.harvard.edu/Directory/search_results.php?v=%s&ltype=lab' % self.id

    def lab_spreadsheet(self):
        if self.id:
            change_url = reverse('view_directory_excel_file', kwargs={})
            return '<a href="%s?primary_lab__id__exact=%s">download Excel (.xls) file</a>' % (change_url, self.id)
        return '(n/a)'
    lab_spreadsheet.allow_tags = True
    
    def __unicode__(self):
        if self.affiliation:
            return '%s (%s)' % (self.name, self.affiliation)
        return self.name

    class Meta:
        ordering = ('name',)


class GraduateProgram(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbrev = models.CharField(max_length=25, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class GraduateYear(models.Model):
    """ Not Applicable, G1, G2, G3, etc."""
    name = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        
class Office(models.Model):

    name = models.CharField(max_length=255)
    link = models.URLField(blank=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class PersonTitle(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)   
    
    
class Person(models.Model):
    lname = models.CharField('Last Name',max_length=225)
    fname = models.CharField('First Name', max_length=225)
    minitial = models.CharField('Middle Initial',max_length=30, blank=True)
    email = models.EmailField(max_length=225)
    
    slug = models.SlugField(blank=True, max_length=255)
    
    second_email = models.EmailField(max_length=225, blank=True)
    phone = PhoneNumberField(blank=True)
    second_phone = PhoneNumberField(blank=True)

    ad_username = models.EmailField('RC username', blank=True, help_text='example: username@rc.harvard.edu')

    fas_username = models.EmailField('FAS username', blank=True, help_text='everyone should have one after migration')
    
    visible = models.BooleanField(default=True)

    room = models.CharField(max_length=75, blank=True)
    building = models.ForeignKey(Building, null=True, blank=True, on_delete=models.PROTECT)

    appointment = models.ForeignKey( AppointmentType, null=True, blank=True, on_delete=models.PROTECT)
    affiliation = models.ForeignKey(PersonAffiliation, help_text='home institution, usually MCB', on_delete=models.PROTECT)
    title = models.ForeignKey(PersonTitle, null=True, blank=True, on_delete=models.PROTECT)
    secondary_titles = models.ManyToManyField(PersonTitle, null=True, blank=True, related_name='secondary titles')

    long_title = models.TextField(blank=True, help_text='optional')

    grad_program = models.ForeignKey(GraduateProgram, null=True, blank=True, on_delete=models.PROTECT)
    grad_year = models.ForeignKey(GraduateYear, null=True, blank=True, on_delete=models.PROTECT)

    office = models.ForeignKey(Office, null=True, blank=True, help_text='optional', on_delete=models.PROTECT)
    secondary_offices = models.ManyToManyField(Office, null=True, blank=True, related_name='secondary offices')
    
    primary_lab = models.ForeignKey(Lab, null=True, blank=True, on_delete=models.PROTECT)
    secondary_labs = models.ManyToManyField(Lab, null=True, blank=True, related_name='secondary labs')
        
    alt_search_term = models.CharField(max_length=255, blank=True, help_text='e.g. "Oshea" if name is "O\'shea"')
    
    profile_image = models.ImageField(upload_to=PROFILE_UPLOAD_TO, help_text='Proportionately Resized to (%s x %s)' % (PERSON_PROFILE_IMAGE_SIZE, PERSON_PROFILE_IMAGE_SIZE),blank=True, null=True)   

    thumb_image = models.ImageField(upload_to=THUMB_UPLOAD_TO, help_text='Auto-filled, Proportionately Resized to (%s x %s)' % (PERSON_PROFILE_THUMB_IMAGE_SIZE, PERSON_PROFILE_THUMB_IMAGE_SIZE),  blank=True, null=True)
    
    
    id_hash = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def save(self):
        if self.id is None:
            super(Person, self).save()

        self.id_hash =  hashlib.sha1('%s%s' % (self.id, str(self.date_modified))).hexdigest()

        # have email with '@mcb.harvard.edu', but not ad_username,
        # make copy email ad_username
        #
        if self.email and self.email.lower().endswith('@mcb.harvard.edu'):
            if self.ad_username and not self.ad_username.lower().endswith('@mcb.harvard.edu'):
                self.ad_username = self.email.lower()

        self.slug = slugify('%s %s %s' % (self.fname, self.minitial, self.lname))

        lst = ['fname', 'lname', 'minitial', 'email', 'second_email', 'phone', 'second_phone']
        for item in lst:
            val = self.__dict__.get(item, None)
            if not val is None:
                self.__dict__.update({item: val.strip() })

        if self.email is not None:
            self.email = self.email.lower()
        if self.second_email is not None:
            self.second_email = self.second_email.lower()
        
        super(Person, self).save()
    
    def address_col(self):
        if self.building:
            return '%s %s' % (self.room, self.building.address_col())
        else:
            return self.room
    
    def __unicode__(self):
        try:
            return '%s, %s' % (self.lname, self.fname)
        except:
            return '%s, %s' % (force_unicode(self.lname), force_unicode(self.fname))
        
            
    def get_absolute_url(self):
        return 'http://www.mcb.harvard.edu/Directory/?pid=%s' % self.id
        
    class Meta:
        ordering = ('lname', 'fname',)  
        verbose_name_plural = 'People'
        
    
    def privacy_info_link(self):
        """Link to HarvardPersonInfo object"""
        if self.id is None:
            return '(no link)'
        
        try:
            hu_info = self.harvardpersoninfo_set.get(person=self)
        except: # HarvardPersonInfo.DoesNotExist:
            return '(no link)'
                  
        change_url = reverse('admin:hu_ldap_harvardpersoninfo_change', args=(hu_info.id,))
        return '<a href="%s">View Privacy Info</a>' % change_url
    privacy_info_link.allow_tags = True

    def address_col_xls(self):
        if self.building:
            return self.building.address_col_xls()
        return None

    def get_building_name(self):
       if self.building:
           return self.building.name
       return None

    def get_secondary_titles(self):
        return SecondaryTitle.objects.filter(person=self)
        
    @staticmethod
    def get_person_text_info(person):
       """Used in pre-delete"""
       if person is None:
           return
       lu = { 'p' : person}    

       info_str =  render_to_string('person/info_dump.txt', lu)
       info_str = info_str.replace('\n\n', '\n').replace('\n\n', '\n').strip()
       return info_str

    @staticmethod
    def save_deleted_person_info(sender, **kwargs):

        person = kwargs.get('instance', None)
        if person is None:
            return

        pinfo = Person.get_person_text_info(person)

        dp = DeletedPerson(lname=person.lname
               , fname=person.fname
               , minitial=person.minitial
               , info=pinfo)
        dp.save()

    def thumb_view(self):
        if self.thumb_image:
            return '<a href="%s"  target="_blank"><img src="%s" style="border:1px solid #333;" alt="thumb" /></a>' % (self.profile_image.url, self.thumb_image.url)
        return '(n/a)'
    thumb_view.allow_tags= True

    def profile_view(self):
        if self.profile_image:
            return '<img src="%s" style="border:1px solid #333;" alt="main" />' % (self.profile_image.url)
        return '(n/a)'
    profile_view.allow_tags= True

    @staticmethod
    def update_image_sizes( sender, **kwargs):
        # if main image is too big, resize it; make a thumbnail image
        #return
        img_rec = kwargs.get('instance', None)
        if img_rec is None or (not img_rec.profile_image) :
            return

        # (1) resize main image
        if img_rec.profile_image.width > PERSON_PROFILE_IMAGE_SIZE or img_rec.profile_image.height > PERSON_PROFILE_IMAGE_SIZE:
            im = Image.open(img_rec.profile_image.file.name)   # open image
            im.thumbnail((PERSON_PROFILE_IMAGE_SIZE, PERSON_PROFILE_IMAGE_SIZE), Image.ANTIALIAS) # resize
            im.save(img_rec.profile_image.file.name, quality=90)   #save
       
        # (2) make a thumbnail
        thumb = Image.open(img_rec.profile_image.file.name)    # open the main image
        thumb.thumbnail((PERSON_PROFILE_THUMB_IMAGE_SIZE, PERSON_PROFILE_THUMB_IMAGE_SIZE), Image.ANTIALIAS)

        thumb_full_dirname = os.path.join(settings.MEDIA_ROOT, THUMB_UPLOAD_TO)
        thumb_full_filename = os.path.join(thumb_full_dirname, os.path.basename(img_rec.profile_image.path) )

        # if needed, make thumb directory
        if not os.path.isdir(thumb_full_dirname):
            os.makedirs(thumb_full_dirname)
        # save file
        ext = thumb_full_filename.split('.')[-1].lower()
        if ext not in ['gif', 'jpeg', 'jpg', 'png']:
            thumb.save(thumb_full_filename, "JPEG", quality=100)
        else:
            thumb.save(thumb_full_filename, quality=100)

        # disconnect save signal, save the ImageRecord, and reconnect signal
        post_save.disconnect(Person.update_image_sizes, sender=Person)        
        
        # update/save django model
        img_rec.thumb_image.name = os.path.join(THUMB_UPLOAD_TO, os.path.basename(img_rec.profile_image.path) ) 
       
        img_rec.save()
        
        # reconnect save signal
        post_save.connect(Person.update_image_sizes, sender=Person)
post_save.connect(Person.update_image_sizes, sender=Person)

class SecondaryTitle(models.Model):
    person = models.ForeignKey(Person)
    title = models.ForeignKey(PersonTitle, on_delete=models.PROTECT)
    sort_order = models.IntegerField()
    
    def __unicode__(self):
        return '%s, %s' % (self.person, self.title)
    
    class Meta:
        ordering = ('person', 'sort_order',)
    
class DeletedPerson(models.Model):
    """Created when a person is deleted from the database"""
    lname = models.CharField('Last Name',max_length=225)
    fname = models.CharField('First Name', max_length=225)
    minitial = models.CharField('Middle Initial',max_length=30, blank=True)
    
    info = models.TextField(blank=True)
    
    delete_date = models.DateTimeField(auto_now_add=True, db_index=True)
       
    def __unicode__(self):
        if self.minitial:
            return '%s, %s %s' % (self.lname, self.fname, self.minitial)
        return '%s, %s' % (self.lname, self.fname)
    
    class Meta:
        ordering = ('lname', 'fname',)  
       
class ResearchInformation(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    research_short_desc = models.TextField()
    research_long_desc = models.TextField(blank=True)
    
    class Meta:
         verbose_name_plural = 'Research Information'
    
    def __unicode__(self):
        return '%s, %s' % (self.person, self.research_short_desc)


from django.db.models.signals import pre_delete, post_save
#from person.person_info_dump import save_deleted_person_info
pre_delete.connect(Person.save_deleted_person_info, sender=Person)

'''
from hu_ldap.models import *
u = HarvardPersonInfo.objects.get(pk=1138)
'''
