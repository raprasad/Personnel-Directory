from personnel_directory.hu_ldap.models import HarvardTitle, HarvardPersonInfo, HarvardAffiliation
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class HarvardTitleAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
admin.site.register(HarvardTitle, HarvardTitleAdmin)

class HarvardAffiliationAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
admin.site.register(HarvardAffiliation, HarvardAffiliationAdmin)


class HarvardPersonInfoAdmin(admin.ModelAdmin):
    
    save_on_top = True
    
    readonly_fields = ( 'person_link'\
                        ,'last_update'\
                       , 'is_student_role', 'is_employee_role', 'is_xid_holder_role'\
                        , 'is_poi_role', 'is_library_borrower_role')
                        
    list_display = ('id', 'lname', 'fname', 'person_link', 'middle_name', 'email', 'phone','is_person_level_4_public', 'is_person_level_5_public'\
            ,'harvardEduFerpaStatus'\
            , 'harvardEduEmployeePrivacy', 'harvardEduStudentPrivacy', 'harvardEduSpecialPrivacy'\
            , 'harvardEduMailPrivacy', 'harvardEduPhonePrivacy', 'harvardEduOfficeAddressPrivacy',)
            
    search_fields = ('lname','fname', 'email', 'phone',)
    list_filter = ('eduPersonAffiliation','harvardEduFerpaStatus', 'harvardEduEmployeePrivacy', 'harvardEduStudentPrivacy', 'harvardEduSpecialPrivacy', 'harvardEduMailPrivacy', 'harvardEduPhonePrivacy', 'harvardEduOfficeAddressPrivacy',)
    filter_horizontal = ( 'eduPersonAffiliation', )
    filter_vertical = ('titles', )
    list_display_links = ( 'id', 'lname',)
    
    fieldsets = [
            ('ldap identifier',  {'fields': [( 'person','uid',), 'person_link', 'last_update',]})
            
            ,('Name / Contact', {'fields': [ ('fname', 'middle_name', 'lname',)\
                ,  ('email',  'phone'), ]})\
                
            ,('Address', {'fields': [ 'postal_address', ( 'zipcode', 'state',), ]})\
            ,('Titles', {'fields': [ 'titles', ]})\

            ,('Roles', {'fields': [ 'eduPersonAffiliation', ('is_student_role', 'is_employee_role',),\
                        ('is_poi_role', 'is_library_borrower_role', 'is_xid_holder_role',), ]})\
                
          
            ,('FERPA', {'fields': [( 'harvardEduFerpaStatus', 'harvardEduFerpaPastStudentIndicator',), ]})\

            ,('Harvard Privacy', {'fields': [('harvardEduSpecialPrivacy', 'harvardEduImagePrivacy', ), ]})\
            ,('Student Privacy', {'fields': [('harvardEduStudentPrivacy', 'harvardEduDormAddressPrivacy', ), ]})\

            ,('Home Privacy', {'fields': [('harvardEduHomePhonePrivacy', 'harvardEduHomeAddressPrivacy',), ]})\

            ,('Work Privacy', {'fields': [ 'harvardEduEmployeePrivacy'\
                    , ( 'harvardEduPhonePrivacy', 'harvardEduFaxPrivacy', 'harvardEduMobilePrivacy',)\
                    ,('harvardEduMailPrivacy', 'harvardEduOfficeAddressPrivacy' ) ]})\
      ]
    
admin.site.register(HarvardPersonInfo, HarvardPersonInfoAdmin)
