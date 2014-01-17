from django.contrib.auth.models import User

from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
from django.db import models
from django.template.defaultfilters import slugify
from person.models import Person, Lab
from tags.models import Tag
from django.core.urlresolvers import reverse

MCB_FACULTY_CATEGORY_ID = 1
AFFILIATE_FACULTY_CATEGORY_ID = 2
EMIRITI_FACULTY_CATEGORY_ID = 4

FACULTY_LINK_TYPE_LAB_WEBSITE = 2

class FacultyCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    sort_order = models.IntegerField(default=5)

    def __unicode__(self):
        return self.name
      
    def save(self):
        self.slug =  slugify(self.name)

        super(FacultyCategory, self).save()        # Call the "real" save() method.
      
    class Meta:
        ordering = ('sort_order', 'name',)
        verbose_name_plural = 'Faculty Categories'

        
class ResearchArea(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, blank=True)

    def save(self):
        self.slug =  slugify(self.name)

        super(ResearchArea, self).save()        # Call the "real" save() method.
      
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        
      
        
     

# Create your models here.
class FacultyMember(Person):
    
    visible_profile = models.BooleanField(default=True)
    
    category = models.ForeignKey(FacultyCategory, null=True)
    
    # helps connect to the personnel directory
    faculty_lab = models.ForeignKey(Lab, null=True, blank=True, on_delete=models.PROTECT)
    
    assistant = models.ForeignKey(Person, blank=True, null=True, help_text='Used to generate phone list.', related_name='faculty assistant')
    
    # pubmed search term: helps make a link to pubmed
    pubmed_search_term =  models.CharField(max_length=255, blank=True, help_text='e.g. "murthy vn"; helps make a link to pubmed')
    
    research_areas = models.ManyToManyField(ResearchArea, null=True, blank=True)
    research_summary = models.TextField(blank=True)

    research_description_title = models.CharField(max_length=255, blank=True)
    research_description = models.TextField(blank=True)
    publication_html = models.TextField(blank=True)
    
    profile_sm_image = models.ImageField(upload_to='faculty/profile', help_text='Small Profile Image (62 x 62)',  blank=True, null=True)
    profile_med_image = models.ImageField(upload_to='faculty/profile', help_text='Medium Profile Image (130 x 154)',blank=True, null=True)   
    
    faculty_member_tag = models.ForeignKey(Tag, null=True, blank=True, related_name='faculty_tag')
    tags = models.ManyToManyField(Tag, null=True, blank=True)#, related_name='tags')

    course_api_id = models.CharField(max_length=100, blank=True, help_text='instructor id in Course API https://manual.cs50.net/HarvardCourses_API')


    def title_list(self):
        l = []
        if self.title:
            l.append('%s' % self.title)

        for t in self.secondarytitle_set.all():
            l.append('%s' % t)

        if l == []:
            return '(not set)'

        return '<br /><br />'.join(l)
    title_list.allow_tags = True
        
    def is_affiliate_faculty(self):
        if self.category and self.category.id == AFFILIATE_FACULTY_CATEGORY_ID:
            return True
        return False

    def get_absolute_url(self):
        return reverse('view_faculty_profile', kwargs={ 'slug' : self.slug }) 
            
    def profile_img_medium(self):
        if not self.profile_med_image:
            return '(no image)'
    
        return '<img src="%s" alt="profile img" />' % (self.profile_med_image.url)
    profile_img_medium.allow_tags = True

    def get_pubmed_link(self):
        if self.pubmed_search_term:
            return 'http://www.ncbi.nlm.nih.gov/pubmed?term=%s' % self.pubmed_search_term
        return None

    def get_link_to_members_in_directory(self):
        if self.faculty_lab:
            return '%s?id_mcb_pdir=1&lab=%s' % (reverse('view_mcb_directory', kwargs={}), self.faculty_lab.id)
        return None
        #/mcb/directory/search/?id_mcb_pdir=1&lab=45
        #view_mcb_directory
        
    def get_lab_website(self):
        #return 'hullo'
        lnks = self.facultylink_set.filter(link_type__id=FACULTY_LINK_TYPE_LAB_WEBSITE)
        if lnks.count() > 0:
            return lnks[0].url
        return None
        

    def profile_img_small(self):
        if not self.profile_sm_image:
            return '(no image)'
    
        return '<img src="%s" alt="profile img" />' % (self.profile_sm_image.url)
    profile_img_small.allow_tags = True

    @staticmethod 
    def get_non_emiriti_faculty():
        return FacultyMember.objects.filter(visible=True\
                , visible_profile=True).exclude(category__id=EMIRITI_FACULTY_CATEGORY_ID)

    @staticmethod 
    def get_emiriti_faculty():
        return FacultyMember.objects.filter(visible=True\
                            , visible_profile=True\
                            , category__id=EMIRITI_FACULTY_CATEGORY_ID)


    class Meta:
        ordering = ('category', 'lname', 'fname',)  
        
    #def save(self):

    #    super(FacultyMember, self).save()        # Call the "real" save() method.
            
class FacultyLinkType(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ('name', )
    
class WebHost(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
          return self.name

    class Meta:
          ordering = ('name', )

class FacultyLink(models.Model):
    faculty_member = models.ForeignKey(FacultyMember) 
    link_type = models.ForeignKey(FacultyLinkType)
    
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    sort_order = models.IntegerField()
    
    # used for lab website inventory
    web_host = models.ForeignKey(WebHost, blank=True, null=True, on_delete=models.PROTECT)
    notes = models.TextField(blank=True, help_text='optional')
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ('faculty_member', 'sort_order', 'name', )


class GalleryImage(models.Model):
    faculty_member = models.ForeignKey(FacultyMember)  
    
    name = models.CharField(max_length=255)
    visible = models.BooleanField(default=True)
    rotate_on_homepage = models.BooleanField(default=True)
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

        return 'click for full size (%sx%s)<br /><a href="%s" target="_blank"><img src="%s" alt="gallery img" width="150" /></a>' % (self.gallery_img.width, self.gallery_img.height, self.gallery_img.url, self.gallery_img.url)
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
