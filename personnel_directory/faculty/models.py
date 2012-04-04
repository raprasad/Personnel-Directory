from django.contrib.auth.models import User

from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
from django.db import models
from django.template.defaultfilters import slugify
from person.models import Person

class FacultyCategory(models.Model):
    name = models.CharField(max_length=255)
    url_name = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name
      
    def save(self):
        self.url_name =  slugify(self.name)

        super(FacultyCategory, self).save()        # Call the "real" save() method.
      
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Faculty Categories'

        
class ResearchArea(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url_name = models.CharField(max_length=255, blank=True)

    def save(self):
        self.url_name =  slugify(self.name)

        super(ResearchArea, self).save()        # Call the "real" save() method.
      
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        
      
        
     

# Create your models here.
class FacultyMember(Person):
    
    visible_profile = models.BooleanField(default=True)
    
    category = models.ForeignKey(FacultyCategory, null=True)
    
    research_areas = models.ManyToManyField(ResearchArea, null=True, blank=True)    # filter_interface=models.HORIZONTAL,
    research_summary = models.TextField(blank=True)

    research_description_title = models.CharField(max_length=255, blank=True)
    research_description = models.TextField(blank=True)
    publication_html = models.TextField(blank=True)
    
    profile_sm_image = models.ImageField(upload_to='faculty/profile', help_text='Small Profile Image (62 x 62), directory: MCB Internet/Faculty/Images/',  blank=True, null=True)
    profile_med_image = models.ImageField(upload_to='faculty/profile', help_text='Medium Profile Image (130 x 154), directory: MCB Internet/Faculty/Images/',blank=True, null=True)   
    
    def get_absolute_url(self):
        return 'http://www.mcb.harvard.edu/Faculty/faculty_profile.php?f=%s' % self.url_name   #howard-berg-c
    
    def profile_img_medium(self):
        if not self.profile_med_image:
            return '(no image)'
    
        return '<img src="%s" alt="profile img" />' % (self.profile_med_image.url)
    profile_img_medium.allow_tags = True

    def profile_img_small(self):
        if not self.profile_sm_image:
            return '(no image)'
    
        return '<img src="%s" alt="profile img" />' % (self.profile_sm_image.url)
    profile_img_small.allow_tags = True

    
    #def save(self):

    #    super(FacultyMember, self).save()        # Call the "real" save() method.
            

class FacultyLink(models.Model):
    faculty_member = models.ForeignKey(FacultyMember) 
    
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    sort_order = models.IntegerField()
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ('faculty_member', 'name', )


class GalleryImage(models.Model):
    faculty_member = models.ForeignKey(FacultyMember)  
    
    name = models.CharField(max_length=255)
    visible = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    teaser = models.TextField(blank=True)

    gallery_img = models.ImageField(help_text='Image (431 x varies), directory: MCB Internet/Faculty/Gallery/', upload_to='faculty/gallery', blank=True, null=True)
    gallery_img_small = models.ImageField(help_text='Image (135 x 85), directory: MCB Internet/Faculty/Gallery/', upload_to='faculty/gallery', blank=True, null=True)
    
    def save(self):
        self.name = self.name.replace('"', '')
    
        lst = ['teaser', 'description', 'name']
        for item in lst:
            val = self.__dict__.get(item, None)
            if not val ==None:
                self.__dict__.update({item: val.strip() })
                
        super(GalleryImage, self).save()        # Call the "real" save() method.
            
    def gallery_image(self):
        if not self.gallery_img:
            return '(no image)'

        return 'forced to 150px wide<br /><img src="%s" alt="gallery img" width="150" />' % (self.gallery_img.url)
    gallery_image.allow_tags = True

    def gallery_image_small(self):
        if not self.gallery_img_small:
            return '(no image)'

        return '&nbsp;<br /><img src="%s" alt="profile img" />' % (self.gallery_img_small.url)
    gallery_image_small.allow_tags = True
    
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ('name', )
