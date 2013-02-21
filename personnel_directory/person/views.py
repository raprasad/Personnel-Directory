from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from django.db.models import Q

from settings import DEBUG as DEBUG 
from common.ajax_util import *
from person.models import *
from person.forms import *
from django.conf import settings 

def is_valid_server(request):
    """Allow json calls from specific servers"""

    #return True
    valid_referers = ('http://127.0.0.1:8000', 
            'https://webapps.sciences.fas.harvard.edu/mcb',
            'http://www.mcb.harvard.edu',)
    
    

    servers_allowed_to_make_json_call = ['140.247.111.70', '140.247.111.165', '140.247.108.24', '127.0.0.1']
    
    # HTTP_REFERER
    #if settings.DEBUG:
    #    return True
    
    if request.META.has_key("HTTP_REFERER"):
        for vr in valid_referers:
            if request.META["HTTP_REFERER"].startswith(vr):
                return True
    
    if request.META["REMOTE_ADDR"] in servers_allowed_to_make_json_call:
        return True 
    
    return False

    
    #elif request.META["SERVER_NAME"] in servers_allowed_to_make_json_call:
    #    return True

    
def view_emailer_form(request):
    lu = { 'lab_form' : LabForm()
          , 'building_form' : BuildingForm()
         , 'office_form' : OfficeForm()
         , 'personnel_category_form' : PersonnelCategoryForm()
         , 'appointment_type_form' : AppointmentTypeForm() 
         , 'graduate_year_form' :GraduateYearForm()
         , 'title_form': TitleForm()
         }
    
    if request.method == 'GET':
        json_retrieve_emails_url = request.GET.get('json_url', None)
        lu.update({'json_retrieve_emails_url' : json_retrieve_emails_url})
    
    return render_to_response('person/view_emailer_form.html', lu, context_instance=RequestContext(request))

def fmt_get_vals(get_str):
    # should only have integers, a delimiter '|', or '-' (as in '-1')
    if get_str is None:
        return []
    
    get_str = str(get_str)
    
    if not get_str.replace('|', '').replace('-', '').isdigit():
        return []
        
    return get_str.split('|')

def show_request_meta_vals(request):
    meta_lines = []
    for key in request.META.keys():
        meta_lines.append('%s - %s' % (key, request.META[key]))
    return HttpResponse( '<br />'.join(meta_lines))
    

def view_email_search_results(request):
    
    #assert(False)
    #print dir(request.META)
    if not is_valid_server(request):
        return get_json_str_as_http_response(request, False, 'Sorry, you cannot access this page. (%s)' % request.META.get("REMOTE_ADDR", 'no REMOTE_ADDR') )

    if request.method == 'GET':
        lab_ids = fmt_get_vals(request.GET.get('lab_ids', '-1'))
        building_ids = fmt_get_vals(request.GET.get('building_ids', '-1'))
        office_ids = fmt_get_vals(request.GET.get('office_ids', '-1'))
        pcat_ids  = fmt_get_vals(request.GET.get('pcat_ids', -1)) 
        appt_ids = fmt_get_vals(request.GET.get('appt_ids', -1)) 
        title_ids = fmt_get_vals(request.GET.get('title_ids', -1)) 
        graduate_year_ids  = fmt_get_vals(request.GET.get('graduate_year_ids', -1)) 
        
        people_with_matching_secondary_titles = SecondaryTitle.objects.filter(title__id__in=title_ids).values_list('person__id', flat=True)
        
        lst = Person.objects.filter(visible=True).filter(Q(primary_lab__id__in=lab_ids) | \
             Q(building__id__in=building_ids) | \
             Q(secondary_labs__id__in=lab_ids) | \
             Q(office__id__in=office_ids) | \
             Q(appointment__id__in=appt_ids) | \
             Q(title__id__in=title_ids) | \
             Q(id__in=people_with_matching_secondary_titles) |\
             Q(grad_year__id__in=graduate_year_ids) | \
             #Q(secondary_titles__id__in=title_ids) | \
             Q(appointment__personnel_category__id__in=pcat_ids) ).values_list('email','lname','fname').distinct().order_by('lname' ,'fname')
        #secondary_labs
        lst = filter(lambda x: x[0] is not None and not x[0]=='', lst)

        email_str = ', '.join(map(lambda x:x[0], lst))
    
        #remove_str = map(lambda x:'x[0], lst)
        
        if len(lst)==1:
            msg = '%s email found' % (len(lst))
        else:
            msg = '%s emails found' % (len(lst))
            
        
        return get_json_str_as_http_response(request, True, msg, lu_vals={'email_str':email_str})
        #return HttpResponse('No attributes to process')
        
        #Person.objects.filter(lab_id=lab_ids.split('|')).all()
        
    else:
        return get_json_str_as_http_response(request, False, 'No attributes to process')
