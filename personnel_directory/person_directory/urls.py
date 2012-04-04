from django.conf.urls.defaults import *


# ajax directory search
urlpatterns = patterns(
    'personnel_directory.person_directory.views'
,    url(r'^search-form-ajax/$', 'view_directory_search_form', name='view_directory_search_form')
,
)

# ajax directory search
urlpatterns += patterns(
    'personnel_directory.person_directory.views_intranet'
,    url(r'^intranet-search-form-ajax/$', 'view_intranet_directory_search_form', name='view_intranet_directory_search_form')
,
)

# lab member xls file - button in the admin
urlpatterns += patterns(
    'personnel_directory.person_directory.view_lab_xls'
,    url(r'^lab-members/(?P<lab_id>(\d){1,4})/xls/$', 'view_lab_member_excel_file', name='view_lab_member_excel_file' )
,
)

