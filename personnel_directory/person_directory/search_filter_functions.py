from django.db.models import Q

from common.msg_util import *
from common.ajax_util import *

from hu_ldap.models import HarvardPersonInfo, HarvardTitle
from person.models import *
from person_directory.forms import *
from faculty.models import FacultyMember, EMIRITI_FACULTY_CATEGORY_ID
from django.core.validators import email_re

import re

QCLAUSE_FILTERS_KEY = 'QCLAUSE_FILTERS_KEY'


def fmt_get_vals(get_str):
    # should only have integers, a delimiter '|', or '-' (as in '-1')
    if get_str is None or get_str in [-1, '-1']:
        return []

    get_str = str(get_str)

    if not get_str.replace('|', '').replace('-', '').isdigit():
        return []

    return get_str.split('|')
        

def is_client_in_harvard_network(request):
    if request is None:
        return False
    
    remote_addr = request.META.get('REMOTE_ADDR', None)
    #print remote_addr[:7]
    if remote_addr is not None:
        if remote_addr[:7] in ['140.247', '128.103']:
            return True
    return False


def get_category_names_for_display(id_lst, modelType, attrNameInModel='name'):
    if id_lst == None or id_lst == []:
        return None
    
    return modelType.objects.filter(id__in=id_lst).values_list(attrNameInModel, flat=True)


def prepare_form_dropdown_criteria_names_and_filter(request):
    """Given a GET request, return a lookup including:
       (a) the selected criteria for display (e.g., selected labs, offices, titles, etc)
       (b) query clauses for retrieving people who match the criteria
    """
    if not request.method == 'GET':
        return None

    lu = {}
    
    # Single Person Info
    pids = fmt_get_vals(request.GET.get('pid', '-1'))
    
    # Lab Info
    lab_ids = fmt_get_vals(request.GET.get('lab', '-1'))
    lu.update({ 'lab_names' : get_category_names_for_display(lab_ids, Lab)})
        
    # Office Info
    office_ids = fmt_get_vals(request.GET.get('office', '-1'))
    lu.update({ 'office_names' : get_category_names_for_display(office_ids, Office) }) 

    # Personnel Category Info
    #pcat_ids  = fmt_get_vals(request.GET.get('pcat_ids', -1)) 
    #lu.update({ 'personnel_category_names' : get_category_names_for_display(pcat_ids, PersonnelCategory) }) 

    # Appointment Type Info
    appt_ids = fmt_get_vals(request.GET.get('appointment_type', -1)) 
    lu.update({ 'appointment_names' : get_category_names_for_display(appt_ids, AppointmentType) }) 

    # Title Info
    title_ids = fmt_get_vals(request.GET.get('title', -1)) 
    lu.update({ 'title_names' : get_category_names_for_display(title_ids, PersonTitle, 'title') }) 

    # Graduate Info
    graduate_year_ids  = fmt_get_vals(request.GET.get('graduate_year', -1)) 
    lu.update({ 'graduate_years' : get_category_names_for_display(graduate_year_ids, GraduateYear ) }) 

    
    clause_dict = { 'primary_lab__id__in' : lab_ids \
                , 'secondary_labs__id__in' : lab_ids \
                , 'office__id__in' : office_ids \
                , 'appointment__id__in' : appt_ids \
                , 'title__id__in' : title_ids \
                #, 'secondary_titles__id__in' : title_ids \
                , 'grad_year__id__in' : graduate_year_ids \
                , 'id__in' : pids \
                }
    qclauses = []
    for k, v in clause_dict.iteritems():
        if v is not None and v is not []:
            qclauses.append( eval('Q(%s=%s)' % (k, v)) )    # e.g. eval('Q(primary_lab__id__in=%s)' % lab_ids)    
            #qclauses.append( eval('{%s:%s}' % (k, v)) )    # e.g. eval('Q(primary_lab__id__in=%s)' % lab_ids)    
                
    qclause_filter = reduce(lambda x,y: x | y, qclauses)
    lu.update({ QCLAUSE_FILTERS_KEY : [qclause_filter] })

    return lu
    

def get_text_search_filter_clauses(search_term):
    ''' Make a list of 'OR' clauses for the queryset filter'''

    if search_term is None:
        return None
        
    attrs_query_like = ['lname', 'fname', 'alt_search_term']
    attrs_phone = ['phone', 'second_phone']
    attrs_email = ['email', 'second_email', 'ad_username']
    
    qclauses = []       # list of 'OR' clauses

    # search first / last names
    if not email_re.match(search_term): # make sure it isn't an email
        for attr in attrs_query_like:  
            qclauses.append( eval('Q(%s__istartswith="%s")' % (attr, search_term)) )
        
    # search email and AD principal names?
    if email_re.match(search_term):
        for attr in attrs_email:  
            qclauses.append( eval('Q(%s__iexact="%s")' % (attr, search_term)) )
        
    # search phone extensions?
    phone_num_pattern = '(\d{3}-\d{2})?\d-\d{4}'
    if re.match(phone_num_pattern, search_term):
        for attr in attrs_phone:  
            qclauses.append( eval('Q(%s__iendswith="%s")' % (attr, search_term)) )  # check extension and full number

    if len(qclauses) > 0:
        qclause_filter = reduce(lambda x,y: x | y, qclauses)
        return qclause_filter
        
    return None

def prepare_form_text_search_criteria_and_filter(search_text):
    """Look up a max of 4 search terms.
        - make a list of OR clauses for each term -> get_text_search_clauses(search_term)
        - AND these filters together
        - pass back the 'search term display' + the filters
    """
    if search_text == None:
        return None
    
    search_text = search_text.strip()
    
    terms = search_text.replace(',', ' ').split()   # split out terms
    terms = terms[0:4]
    lu = { 'search_vals' : terms }
    
    qs_filters = []
    for st in terms:
        qs_filter = get_text_search_filter_clauses(st)
        if qs_filter is not None:
            qs_filters.append(qs_filter)

    if len(qs_filters) == 0:
        return None
        
    lu.update({ QCLAUSE_FILTERS_KEY : qs_filters})
    return lu

'''
    return " ( lname LIKE '{$srch_param}%' " 
			. " OR fname LIKE '{$srch_param}%'"
			. " OR alt_search_term LIKE '{$srch_param}%'"
			. " OR phone = '{$srch_param}' "
			. " OR ad_username LIKE '{$srch_param}' "
			. " OR ad_username = '{$srch_param_ad_name}' "
			. " OR right(phone, 6) = '{$srch_param}'"
			. " OR email = '{$srch_param}'"
			. " OR second_email = '{$srch_param}'"
			. ")";

'''

def retrieve_directory_search_results(request, is_departmental_intranet=False):
    lu = {}

    # Is this a GET request
    if not request.method == 'GET':
        lu.update({'ERR_nothing_selected': True }); return lu
    
    # Has a choice been made
    choice_selected = False
    for key, val in request.GET.iteritems():
        if not (val=='-1' or val=='Go') and not key=='jsoncallback':        # make sure something has been chosen/selected
            choice_selected = True
    if not choice_selected:
        lu.update({'ERR_nothing_selected': True }); return lu
    
    is_internal_client = is_client_in_harvard_network(request)
    #for k,v in request.GET.iteritems():
    #    print '%s : [%s]' % (k, v)
        

    # from the GET dict, return result labels and a queryset filter consisting of Q clauses

    
    search_text = request.GET.get('search_term', None)      # for text search
    if search_text is not None:
        search_text= search_text.replace('\\', '').replace('/', '')
    
    #Is this a text search?
    if search_text is not None and not search_text.strip() == '':
        # Yes, it's a text search
        form_info_dict = prepare_form_text_search_criteria_and_filter(search_text)    
    else:        
        # Search via dropdown boxes or 'pid' (a person id)
        form_info_dict = prepare_form_dropdown_criteria_names_and_filter(request)

    if form_info_dict is None:
        #msgt('--2--')
        lu.update({'ERR_nothing_selected': True }); return lu
    
    try:
        qclause_filters = form_info_dict.pop(QCLAUSE_FILTERS_KEY)
    except KeyError:
        lu.update({'ERR_query_clause_error': True }); return lu
        
    # add display results to the template lu
    lu.update(form_info_dict)

    # retreive people based on form criteria
    people = Person.objects.select_related('office', 'primary_lab', 'title', 'appointment', 'affiliation', 'secondary_labs', 'grad_year').filter(visible=True)
    for qclause_filter in qclause_filters:
        people = people.filter(qclause_filter)
    
    people = people.distinct().order_by('lname' ,'fname')
   
    people_lst= add_privacy_info_and_remove_blocked_persons(people, is_internal_client, is_departmental_intranet)

    add_secondary_labs(people_lst, qclause_filters)
    add_secondary_titles(people_lst, qclause_filters)
    add_faculty_profile_flag(people_lst)

    last_get = request.GET.copy()
    if last_get.has_key('jsoncallback'): last_get.pop('jsoncallback')
    last_get_str = '&'.join( map(lambda x: '%s=%s' % (x[0],x[1]), last_get.items()) )
    
    person_cnt =  len(people_lst)
    
    if person_cnt > 5:
        lu.update({ 'more_than_5_people_found' : True })

    lu.update({ 'people' : people_lst \
            , 'person_cnt' : person_cnt
            , 'last_get_str' : last_get_str })

    return lu

    
def add_faculty_profile_flag(people_lst):
    """To reduce ManyToMany-related queries in template, preload secondary title information"""

    # pull ids of faculty with profiles with second titles
    faculty_ids = FacultyMember.objects.filter(visible=True, visible_profile=True).exclude(category__id=EMIRITI_FACULTY_CATEGORY_ID).values_list('id', flat=True)
    
    for p in people_lst:
        if p.id in faculty_ids:
            p.has_faculty_profile= True
        else:
            p.has_faculty_profile = False
            

def add_secondary_titles(people_lst, qclause_filters):
    """To reduce ManyToMany-related queries in template, preload secondary title information"""

    # pull ids of people with second titles
    ids_of_people_with_second_titles = SecondaryTitle.objects.filter(person__visible=True).values_list('person__id', flat=True)

    if len(ids_of_people_with_second_titles) == 0:
        return

    # find them in the selected person list
    for p in people_lst:
        if p.id in ids_of_people_with_second_titles:        # if they match, add the second title(s) directly
            p.second_titles = []
            for other_title in p.get_secondary_titles():
                p.second_titles.append(other_title.title)
    #------------------------------------------------
    #   code using obsolete "secondary_titles"
    #------------------------------------------------
    # pull ids of people with second titles
    """
    second_title_ids = Person.objects.exclude(secondary_titles=None).filter(visible=True)
    
    for qclause_filter in qclause_filters:
        second_title_ids = second_title_ids.filter(qclause_filter)

    second_title_ids = second_title_ids.values_list('id', flat=True)
    

    if len(second_title_ids) == 0:
        return

    # go through each id of person with 2nd title 
    for pid in second_title_ids:
        # find them in the selected person list
        for p in people_lst:
            if pid == p.id: # if they match, add the second lab directly
                p.second_titles = []
                #for other_title in p.secondary_titles.all():
                for other_title in p.secondarytitle_set.all():
                    p.second_titles.append(other_title.title)
    """

def add_secondary_labs(people_lst, qclause_filters):
    """To reduce ManyToMany-related queries in template, preload secondary lab information"""

    # pull ids of people with second labs
    second_lab_ids = Person.objects.exclude(secondary_labs=None).filter(visible=True)
    
    for qclause_filter in qclause_filters:
        second_lab_ids = second_lab_ids.filter(qclause_filter)
        
    second_lab_ids = second_lab_ids.values_list('id', flat=True)

    if len(second_lab_ids) == 0:
        return

    # go through each id of 2nd lab person
    for pid in second_lab_ids:
        # find them in the selected person list
        for p in people_lst:
            if pid == p.id: # if they match, add the second lab directly
                p.second_labs = []
                for other_lab in p.secondary_labs.all():
                    p.second_labs.append(other_lab)
    
    
    
    

def add_privacy_info_and_remove_blocked_persons(people, is_internal_client=True, is_departmental_intranet=False):
    """Given a queryset of people: 
    (1) add an associated HarvardPersonInfo object--if it exists
    (2) use the HarvardPersonInfo object to see phone, email, and office privacy variables ('is_phone_private', 'is_email_private', etc)
    """
    #msgt('add_privacy_info.  is_internal_client: [%s]' % is_internal_client)
    
    # retrieve harvard person info records -- these contain privacy info
    pinfo_lst = HarvardPersonInfo.objects.filter(person__id__in=people.values_list('id', flat=True))
    
    # put the people into a lookup
    pinfo_dict = dict([(obj.person_id, obj) for obj in pinfo_lst])
    
    # attach harvard info to people
    for person in people:
        person.hu_info = pinfo_dict.get(person.id, None)
        
        # set privacy values for use in templates
        privacy_lu = { 'harvardEduPhonePrivacy':'is_phone_private'
                    , 'harvardEduMailPrivacy': 'is_email_private' 
                    , 'harvardEduOfficeAddressPrivacy': 'is_office_address_private' 
                    }
                    
        # add attribute-level privacy info here--even though these people may be blocked completely in next check
        #            
        for attr, privacy_attr in privacy_lu.iteritems():
            if person.hu_info:
                    if person.hu_info.__dict__.get(attr, 1) < 4:            # (a) less than 4 -> cannot display   (if not found, default to lowest level)
                        person.__dict__.update({privacy_attr : True})
                    elif person.hu_info.__dict__.get(attr, 1) == 4 and is_departmental_intranet:  # (b) equal to 4 and logged in -> display
                        # logged into mcb
                        person.__dict__.update({privacy_attr : False})
                        
                    elif person.hu_info.__dict__.get(attr, 1) == 4 and not is_internal_client:  # equal to 4 and outside harvard network -> cannot display
                        person.__dict__.update({privacy_attr : True})
                    else:
                        person.__dict__.update({privacy_attr : False})
            else:
                person.__dict__.update({privacy_attr : False})

        #msgt(person)
        #for attr, privacy_attr in privacy_lu.iteritems():
        #    if person.hu_info:
        #        msg('%s - [%s][%s]' % (attr, person.hu_info.__dict__.get(attr, '?'), person.__dict__.get(privacy_attr)))

    # Depending on whether the client is in the Harvard network, 
    # show people with level 4 or level 5 privacy
    #
    # For the departmental intranet, only restrict FERPA blocks
    if is_departmental_intranet:
        people_lst = filter(lambda p: not (p.hu_info is not None and p.hu_info.has_ferpa_restriction()), people) 
        return people_lst
                
    elif is_internal_client:  
        # level 4 - internal network
        people_lst = filter(lambda p: (p.hu_info is None) or (p.hu_info and p.hu_info.is_person_level_4_public()), people)    # only display people with no harvard info or level 4 info        

    else:
        # level 5 public
        people_lst = filter(lambda p: (p.hu_info is None) or (p.hu_info and p.hu_info.is_person_level_5_public()), people)    # only display people with no harvard info or level 5 info
        
    return people_lst
