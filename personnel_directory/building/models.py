from django.db import models
from django.contrib.localflavor.us.models import USStateField
from django.template.defaultfilters import slugify


class Building(models.Model):
    """Building Name, Nickname, and Address
    e.g. Northwest Building, NW, etc, etc"""
    abbrev = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)

    website = models.URLField(blank=True, help_text='e.g. website for NW building')
    map_link = models.URLField(blank=True)
    
    addr1 = models.CharField(max_length=255)
    addr2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state = USStateField()
    zipcode = models.CharField(max_length=25)

    img_name = models.CharField(max_length=255, blank=True)


    def __unicode__(self):
        return '%s, %s %s' % (self.name, self.addr1, self.city)

    def save(self):
        self.slug =  slugify(self.name)
        super(Building, self).save()        # Call the "real" save() method.

    class Meta:
        ordering = ('name',)

    def address_col_for_web(self):
        if self.addr2:
            return '''%s
            <br />%s
            <br />%s
            <br />%s, %s &nbsp;%s''' % (self.name, self.addr1, self.addr2, self.city, self.state, self.zipcode)
        else:
            return '''%s
            <br />%s
            <br />%s, %s &nbsp;%s''' % (self.name, self.addr1,self.city, self.state, self.zipcode)
            
    def address_col(self):
        if self.addr2:
            return '%s, %s, %s %s %s, %s' % (self.name, self.addr1, self.addr2, self.city, self.zipcode, self.state)
        else:
            return '%s, %s, %s %s, %s' % (self.name, self.addr1, self.city, self.zipcode, self.state)

    def address_col_xls(self):
        if self.addr2:
            return '%s\n%s\n%s, %s %s' % (self.addr1, self.addr2, self.city, self.state, self.zipcode)
        else:
            return '%s\n%s, %s %s' % ( self.addr1, self.city, self.state, self.zipcode)
    
   