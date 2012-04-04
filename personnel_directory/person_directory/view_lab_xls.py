from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.db.models import Q

import xlwt

from datetime import datetime

from person.models import Lab, Person
from person_directory.lab_xls_maker import make_lab_member_roster



def view_lab_member_excel_file(request, lab_id=None):
    """From the Django admin view of a Person->Lab object, generate an Excel spreadsheet"""
    if not (request.user.is_authenticated() and request.user.is_staff):  
        return HttpResponse('not accessible')
    
    try:
        lab = Lab.objects.get(pk=lab_id)
    except:
        return HttpResponse('Sorry!  The lab was not found!  <br />Please press the back button on your browser.')
        
    people = Person.objects.filter(Q(primary_lab__id=lab.id) | \
                 Q(secondary_labs=lab.id)).order_by('lname', 'fname')
   
    if people.count() == 0:
        return HttpResponse('Sorry!  No trainees are in this list.<br />Please press the back button on your browser.')
    
    book = xlwt.Workbook(encoding="utf-8")
    # With a workbook object made we can now add some sheets.
    sheet1 = book.add_sheet(slugify(lab.name[0:30]))

    date_obj = datetime.now()
    info_line = "Generated on %s" % (date_obj.strftime('%m/%d/%Y - %I:%M %p'))

    sheet1 = make_lab_member_roster(sheet1, info_line, people, lab)

    # create response object
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=lab_%s_%s.xls' % (lab.url, date_obj.strftime('%m%d-%I-%M%p').lower())
    
    # send .xls spreadsheet to response stream
    book.save(response)
    return response
    



    