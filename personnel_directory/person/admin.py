from person.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _



class PersonAffiliationAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)

admin.site.register(PersonAffiliation, PersonAffiliationAdmin)

class PersonnelCategoryAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    
admin.site.register(PersonnelCategory, PersonnelCategoryAdmin)

class SecondaryTitleAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('title',)
    list_display= ('title', 'person', 'sort_order')
admin.site.register(SecondaryTitle, SecondaryTitleAdmin)



class AppointmentTypeAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'description', 'personnel_category')
    search_fields = ('name', 'description',)
    list_filter = ('personnel_category',)
admin.site.register(AppointmentType, AppointmentTypeAdmin)

"""
class BuildingAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display= ('name','abbrev',  'addr1', 'state', 'zipcode')
    search_fields = ('name', )
admin.site.register(Building, BuildingAdmin)
"""

class LabAdmin(admin.ModelAdmin):
    save_on_top = True
    readonly_fields = ('lab_spreadsheet', )
    list_display = ('name', 'affiliation', 'lab_spreadsheet',)
    list_filter = ('affiliation', )
    search_fields = ('name',)
admin.site.register(Lab, LabAdmin)


class GraduateProgramAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'abbrev', 'description',)
    search_fields = ('name', 'abbrev', 'description',)
admin.site.register(GraduateProgram, GraduateProgramAdmin)

class OfficeAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
admin.site.register(Office, OfficeAdmin)


class GraduateYearAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
admin.site.register(GraduateYear, GraduateYearAdmin)


class PersonTitleAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('title',)
admin.site.register(PersonTitle, PersonTitleAdmin)

class ResearchInformationInline(admin.TabularInline):
    model = ResearchInformation
    max_num =1
    
class SecondaryTitleInline(admin.TabularInline):
    model = SecondaryTitle
    extra = 0
    
    
class PersonAdmin(admin.ModelAdmin):
    save_on_top = True
    readonly_fields = ['privacy_info_link', 'date_added', 'date_modified', 'id_hash', 'profile_view', 'thumb_view']
    list_display = ('lname', 'fname', 'minitial', 'privacy_info_link', 'email', 'phone','affiliation', 'appointment','title','primary_lab', 'grad_year','office', 'visible')
    search_fields = ('lname','fname',  'email', 'second_email' )
    list_filter = ( 'visible','building', 'appointment','affiliation', 'grad_year','grad_program', 'office', 'primary_lab')
    filter_horizontal = ( 'secondary_labs',)
    #filter_vertical = ('secondary_titles',)
    inlines = [SecondaryTitleInline, ResearchInformationInline, ]
    
    # list_editable = ('email','phone','fname',)# 'lname',)
    #positions = ('labs',)
    fieldsets = [
          ('Name',               {'fields': ['fname', 'minitial', 'lname', 'privacy_info_link'  ]}),
          ('Email', {'fields': ['email', 'second_email',]}),
          ('Phone', {'fields': ['phone', 'second_phone', ]}),
          ('User Names', {'fields': ['ad_username', 'fas_username',]}),
          ('Visible on Web', {'fields': ['visible', ]}),
          ('Physical Address', {'fields': ['room', 'building']}),
          ('Position Information', {'fields': ['appointment', 'affiliation', 'office', 'title',]}), #'secondary_titles']}),
          ('Lab', {'fields': ['primary_lab', 'secondary_labs']}),
          ('Graduate Information', {'fields': ['grad_program', 'grad_year',]}),
          ('Extra', {'fields': ['alt_search_term',]}),
          ('Images', {'fields': ['profile_image', 'thumb_image', 'profile_view', 'thumb_view']}),
          ('Internal Info', {'fields': ['date_added', 'date_modified', 'id_hash']}),

      ]
    
admin.site.register(Person, PersonAdmin)


class DeletedPersonAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('lname', 'fname', 'minitial', 'delete_date')
    search_fields = ('lname','fname', 'info', )
admin.site.register(DeletedPerson, DeletedPersonAdmin)

class ResearchInformationAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('person', 'research_short_desc', )
    search_fields = ('research_short_desc','research_long_desc', )
    
admin.site.register(ResearchInformation, ResearchInformationAdmin)

