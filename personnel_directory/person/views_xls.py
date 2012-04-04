from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.db.models import Q

import xlwt

from personnel_directory.common.time_util import get_datetime_now

from personnel_directory.person.models import Lab, Person, PersonTitle
from personnel_directory.person.person_xls_maker import make_person_roster


def add_secondary_titles(people_lst, qclause_filters):
    """To reduce ManyToMany-related queries in template, preload secondary title information"""

    # pull ids of people with second titles
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
                for other_title in p.secondary_titles.all():
                    p.second_titles.append(other_title.title)


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





def view_directory_excel_file(request):
    """From the Django admin view of a Person->Lab object, generate an Excel spreadsheet"""
    if not (request.user.is_authenticated() and request.user.is_staff):  
        return Http404('404 - Page Not Found')
    
    if request.method == 'GET':  
        kwargs = {}
        for x,y in request.GET.iteritems():
            if not str(x) in ['ot', 'o', 'q']:
                kwargs.update({str(x):str(y)})
        #print kwargs
        try:
            people = Person.objects.select_related('office', 'building', 'primary_lab', 'title', 'appointment', 'affiliation', 'secondary_titles', 'secondary_labs', 'grad_program', 'grad_year').filter(**kwargs).order_by('lname','fname')
        except:
            people = Person.objects.select_related('office', 'building', 'primary_lab', 'title', 'appointment', 'affiliation', 'secondary_titles', 'secondary_labs', 'grad_program', 'grad_year').all().order_by('lname','fname')    
    else:
        people = Person.objects.select_related('office', 'building', 'primary_lab', 'title', 'appointment', 'affiliation', 'secondary_titles', 'secondary_labs', 'grad_program', 'grad_year').filter(visible=True).order_by('lname', 'fname')
   
    if people.count() == 0:
        return HttpResponse('Sorry!  No trainees are in this list.<br /><br />Please press the back button on your browser.')
    
    book = xlwt.Workbook(encoding="utf-8")
    # With a workbook object made we can now add some sheets.
    sheet1 = book.add_sheet(slugify('MCB People'))

    date_obj = get_datetime_now()
    info_line = "Generated on %s" % (date_obj.strftime('%m/%d/%Y - %I:%M %p'))

    sheet1 = make_person_roster(sheet1, info_line, people)

    # create response object
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mcb_listing_%s.xls' % ( date_obj.strftime('%m%d-%I-%M%p-%S').lower())
    
    # send .xls spreadsheet to response stream
    book.save(response)
    return response
    
    # For testing/viewing queries
    #return render_to_response('sql_query_debug.html', {}, context_instance=RequestContext(request))
