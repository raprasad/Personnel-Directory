from django.conf.urls.defaults import *


urlpatterns = patterns(
    'faculty.views',   
    (r'profile/(?P<slug>(-|\w|_){1,150})/$', 'view_faculty_profile'),

    (r'all/$', 'view_faculty_list'),
   
)

