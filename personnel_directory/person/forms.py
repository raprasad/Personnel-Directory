from django import forms 
from person.models import Person, Lab, Office, MCB_AFFILIATION_ID, PersonnelCategory, AppointmentType, PersonTitle, GraduateYear
from building.models import Building


LAB_CHOICES = map(lambda x: (x.id, x.name_affil), Lab.objects.filter(affiliation__id=MCB_AFFILIATION_ID))
class LabForm(forms.Form):
    all_labs = forms.BooleanField(required=False)
    lab = forms.ChoiceField(label='Labs', choices=LAB_CHOICES
            , widget=forms.CheckboxSelectMultiple(attrs={'class':'lab_choice cbox',})
        )
    

BUILDING_CHOICES = map(lambda x: (x.id, x.name), Building.objects.all())
class BuildingForm(forms.Form):
    all_buildings = forms.BooleanField(required=False)
    buiding = forms.ChoiceField(label='Buildings', choices=BUILDING_CHOICES
            , widget=forms.CheckboxSelectMultiple(attrs={'class':'building_choice cbox',})
        )

OFFICE_CHOICES = map(lambda x: (x.id, x.name), Office.objects.all())
class OfficeForm(forms.Form):
    all_offices = forms.BooleanField(required=False)

    office = forms.ChoiceField(label='Offices', choices=OFFICE_CHOICES
            , widget=forms.CheckboxSelectMultiple(attrs={'class':'office_choice cbox',})
        )  
    
        
PERSONNEL_CATEGORY_CHOICES = map(lambda x: (x.id, x.name), PersonnelCategory.objects.all())
class PersonnelCategoryForm(forms.Form):
    all_personnel_categories = forms.BooleanField(required=False)

    personnel_category = forms.ChoiceField(label='Personnel Category', choices=PERSONNEL_CATEGORY_CHOICES
            , widget=forms.CheckboxSelectMultiple(attrs={'class':'pcat_choice cbox',})
        )
        

APPOINTMENT_TYPE_CHOICES = map(lambda x: (x.id, x.name), AppointmentType.objects.all())
class AppointmentTypeForm(forms.Form):
    all_appointment_types = forms.BooleanField(required=False)

    appointment_type = forms.ChoiceField(label='Appointment Type', choices=APPOINTMENT_TYPE_CHOICES
          , widget=forms.CheckboxSelectMultiple(attrs={'class':'appt_choice cbox',})
      )


def get_grad_year_choices():
    grad_year = Person.objects.filter(visible=True).exclude(grad_year__id=None).values_list('grad_year__id', flat=True)
    grad_year_dict = {}
    for gyear in grad_year:
        grad_year_dict.update({ gyear:1 })
    #grad_year_menu = 
    
    GRAD_YEAR_CHOICES = map(lambda x: (x.id, x.name), GraduateYear.objects.filter(id__in=grad_year_dict.keys()))
    return GRAD_YEAR_CHOICES
    if json_format:
        let_menu = map(lambda x: '"%s"' % x, letter_menu)
        return '''"letters_for_menu" : [%s]''' % (','.join(let_menu))

    return letter_menu

#GRAD_YEAR_CHOICES = map(lambda x: (x.id, x.name), GraduateYear.objects.all())
class GraduateYearForm(forms.Form):
  all_graduate_years = forms.BooleanField(required=False)

  graduate_year = forms.ChoiceField(label='Graduate Year', help_text='(years displayed have active students)', choices=get_grad_year_choices()
        , widget=forms.CheckboxSelectMultiple(attrs={'class':'graduate_year_choice cbox',})
    )

SELECTED_TITLE_CHOICES = map(lambda x: (x.id, x.title), PersonTitle.objects.filter(id__in=[198, 173, 212]))
class TitleForm(forms.Form):
    all_titles = forms.BooleanField(required=False)

    title = forms.ChoiceField(label='Title', choices=SELECTED_TITLE_CHOICES
         , widget=forms.CheckboxSelectMultiple(attrs={'class':'title_choice cbox',})
     )

'''
class RemoveEmailForm(forms.Form):

  title = forms.ChoiceField(label='Title', choices=SELECTED_TITLE_CHOICES
          , widget=forms.CheckboxSelectMultiple(attrs={'class':'title_choice cbox',})
      )
'''