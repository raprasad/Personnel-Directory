from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils import simplejson

from django.db.models import Q

from settings import DEBUG as DEBUG 

from common.msg_util import *
from common.ajax_util import *

from hu_ldap.models import HarvardPersonInfo, HarvardTitle
from person.models import *

from person_directory.forms import *
from person_directory.search_filter_functions import retrieve_directory_search_results

from django.conf import settings
from django.db import connection



def view_intranet_directory_search_form(request, render_as_json=True):
    """Send the form, or form submitted results as JSON encoded HTML
    
    This page is accessed after logging into the intranet.  As a result a check is made that the request is made from the intranet server.
    """
    
    lu = {}
    callback = request.GET.get('jsoncallback', None)

    if not request.META["REMOTE_ADDR"] in SERVERS_ALLOWED_TO_MAKE_JSON_CALL:
        return get_json_str_as_http_response2(request, False, msg='Sorry!  No access from this client.', json_str='', callback=callback)
           

        
    if request.method == 'GET' and request.GET.has_key('id_mcb_personnel_dir'):  
        results_dict = retrieve_directory_search_results(request, is_departmental_intranet=True)
        
        #msgt('results_dict: %s' % results_dict)
        if results_dict.has_key('ERR_nothing_selected'):
            lu.update(results_dict)
        else:
            if settings.DEBUG:
                results_dict.update({ 'queries' : connection.queries })
            if not render_as_json:
                return HttpResponse(render_to_string('person_directory/intranet/view_internal_search_results.html', results_dict))
            page_str = render_to_string_remove_spaces('person_directory/intranet/view_internal_search_results.html', results_dict)

                
            return get_json_str_as_http_response2(request, True, msg='', json_str=',"page_str" : %s' % simplejson.dumps(page_str), callback=callback)

    lu.update( { 
            'text_form': PersonSearchForm()
         , 'lab_form' : LabForm()
         , 'office_form' : OfficeForm()
        # , 'personnel_category_form' : PersonnelCategoryForm()
         , 'appointment_type_form' : AppointmentTypeForm() 
         , 'title_form': TitleForm()
         , 'graduate_year_form' :GraduateYearForm()
         })

    if not render_as_json:
        return HttpResponse(render_to_string('person_directory/intranet/view_intranet_search_form.html', lu))

    page_str = render_to_string_remove_spaces('person_directory/intranet/view_intranet_search_form.html', lu)    
    return get_json_str_as_http_response2(request, True, msg='', json_str=',"page_str" : %s' % simplejson.dumps(page_str), callback=callback)
    
    #return render_to_response('person_directory/view_search_form.html', lu, context_instance=RequestContext(request))

