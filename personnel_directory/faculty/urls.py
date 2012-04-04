from django.conf.urls.defaults import *


urlpatterns = patterns(
    'faculty.views',   
#    (r'profile/(?P<faculty_id>(\d{1,4}))/$', 'view_faculty_profile'),
    (r'all/$', 'view_faculty_list'),
   
)

