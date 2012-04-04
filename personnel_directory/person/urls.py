from django.conf.urls.defaults import *
#from person.views_lab_feed import LabFeed

urlpatterns = patterns(
    'personnel_directory.person.views',

    url(r'^emailer-form/$', 'view_emailer_form', name='view_emailer_form' ),

     url(r'^email-search/$', 'view_email_search_results', name='view_email_search_results' ),
     
     #url(r'^email-meta/$', 'show_request_meta_vals', name='show_request_meta_vals' ),
     
)


urlpatterns += patterns(
    'personnel_directory.person.views_xls',
    url(r'^person-xls/$', 'view_directory_excel_file', name='view_directory_excel_file' ),

)