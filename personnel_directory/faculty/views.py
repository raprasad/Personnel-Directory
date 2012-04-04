from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import loader, Context
from faculty.models import *


 

def view_faculty_list(request):
    if not request.user.is_authenticated():
        return HttpResponse('not logged in')

    # Load basic info for header, etc
    #
    lu = { 'faculty' : FacultyMember.objects.all() 
            }
    
    
    return render_to_response('faculty/view_titles.html', lu)
