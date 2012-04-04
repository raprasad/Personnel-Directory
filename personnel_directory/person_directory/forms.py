from django import forms 
from person.models import Person, Lab, Office, MCB_AFFILIATION_ID, PersonnelCategory, AppointmentType, PersonTitle, GraduateYear


class PersonSearchForm(forms.Form):
    search_term = forms.CharField(label='Search', help_text='You can search by part or all of a person\'s name, a full email address or phone (extension "5-2300" or full number "617-495-2300").')


LAB_CHOICES = [(-1, 'Labs')] + [(x.id, x.name_affil) for x in Lab.objects.filter(affiliation__id=MCB_AFFILIATION_ID)]
class LabForm(forms.Form):
    #all_labs = forms.BooleanField(required=False)
    lab = forms.ChoiceField(label='', choices=LAB_CHOICES
            , widget=forms.Select(attrs={'class':'lab_choice cbox',})
        )
    
 
OFFICE_CHOICES = [(-1, 'Offices')] + [(x.id, x.name) for x in Office.objects.all()]
class OfficeForm(forms.Form):
    #all_offices = forms.BooleanField(required=False)

    office = forms.ChoiceField(label='', choices=OFFICE_CHOICES
            , widget=forms.Select(attrs={'class':'office_choice cbox',})
        )  
    
        
#PERSONNEL_CATEGORY_CHOICES = map(lambda x: (x.id, x.name), PersonnelCategory.objects.all())
PERSONNEL_CATEGORY_CHOICES = [(-1, 'Personnel Categories')] + [(x.id, x.name) for x in PersonnelCategory.objects.all()]

class PersonnelCategoryForm(forms.Form):
    #all_personnel_categories = forms.BooleanField(required=False)

    personnel_category = forms.ChoiceField(label='', choices=PERSONNEL_CATEGORY_CHOICES
            , widget=forms.Select(attrs={'class':'pcat_choice cbox',})
        )
        

APPOINTMENT_TYPE_CHOICES = [(-1, 'Appointment Types')] + [(x.id, x.name) for x in AppointmentType.objects.all()]
class AppointmentTypeForm(forms.Form):
    #all_appointment_types = forms.BooleanField(required=False)

    appointment_type = forms.ChoiceField(label='', choices=APPOINTMENT_TYPE_CHOICES
          , widget=forms.Select(attrs={'class':'appt_choice cbox',})
      )


def get_grad_year_choices():
    grad_year = Person.objects.filter(visible=True).exclude(grad_year__id=None).values_list('grad_year__id', flat=True)
    grad_year_dict = {}
    for gyear in grad_year:
        grad_year_dict.update({ gyear:1 })
    #grad_year_menu = 
    
    GRAD_YEAR_CHOICES = [(-1, 'Graduate Students')] + [(x.id, x.name) for x in GraduateYear.objects.filter(id__in=grad_year_dict.keys())]

    return GRAD_YEAR_CHOICES
    if json_format:
        let_menu = map(lambda x: '"%s"' % x, letter_menu)
        return '''"letters_for_menu" : [%s]''' % (','.join(let_menu))

    return letter_menu

#GRAD_YEAR_CHOICES = map(lambda x: (x.id, x.name), GraduateYear.objects.all())
class GraduateYearForm(forms.Form):
  #all_graduate_years = forms.BooleanField(required=False)

  #help_text='(years displayed have active students)'
  graduate_year = forms.ChoiceField(label='',  choices=get_grad_year_choices()
        , widget=forms.Select(attrs={'class':'graduate_year_choice cbox',})
    )

SELECTED_TITLE_CHOICES = [(-1, 'Selected Titles')] + [(x.id, x.title) for x in PersonTitle.objects.filter(id__in=[198, 173, 212])]
class TitleForm(forms.Form):
    #all_titles = forms.BooleanField(required=False)

    title = forms.ChoiceField(label='', choices=SELECTED_TITLE_CHOICES
         , widget=forms.Select(attrs={'class':'title_choice cbox',})
     )
