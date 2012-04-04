from django.contrib.syndication.views import Feed
from django.db.models import Q
from django.shortcuts import get_object_or_404
import datetime

from person.models import Person, Lab

class LabFeed(Feed):
    description_template = 'person/feeds/lab_feed.html'

    def get_object(self, request, lab_id):
        return get_object_or_404(Lab, pk=lab_id)

    def title(self, obj):
        return "Members of the %s Lab" % obj
        
    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return 'Below are current members of the %s Lab' % obj
    
    def item_pubdate(self, item):
        return datetime.datetime.now()
        
    #def item_description(self, item):
    #    return item.description
    
    def items(self, obj):
        return  Person.objects.filter( Q(primary_lab__id=obj.id) | Q(secondary_labs=obj.id)  ).filter(visible=True).all()    
        #return  Person.objects.filter(primary_lab__id=obj.id).all()  