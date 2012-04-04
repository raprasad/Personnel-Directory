from person.models import SecondaryTitle
from faculty.models import *
from person.admin import PersonAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class FacultyLink_Inline(admin.TabularInline):
    model = FacultyLink
    extra = 0

class GalleryImage_Inline(admin.TabularInline):
    model = GalleryImage
    extra = 0

class ResearchAreaAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display= ('name', 'url_name' )    
admin.site.register(ResearchArea, ResearchAreaAdmin)

class FacultyLinkAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display= ('faculty_member', 'name', )   
admin.site.register(FacultyLink, FacultyLinkAdmin)


class SecondaryTitleInline(admin.TabularInline):
  model = SecondaryTitle
  extra = 0

class FacultyMemberAdmin(PersonAdmin):
    inlines = [SecondaryTitleInline, FacultyLink_Inline, GalleryImage_Inline]    # FacultyPublicationInline]
    save_on_top = True
    readonly_fields = ['privacy_info_link', 'profile_img_small', 'profile_img_medium']
    list_display = ('lname', 'fname', 'minitial', 'profile_img_small', 'profile_img_medium', 'email', 'phone','category', 'affiliation', 'appointment','title', 'visible')
    search_fields = ('lname','fname',  'email', 'second_email' )
    list_filter = ( 'visible','visible_profile', 'category', 'research_areas','affiliation', )
    filter_horizontal = ( 'secondary_labs', 'research_areas',)
    filter_vertical = ('secondary_titles', )
    #inlines = [ResearchInformationInline, ]
    
    # list_editable = ('email','phone','fname',)# 'lname',)
    #positions = ('labs',)
    fieldsets = [
          ('Name',               {'fields': ['fname', 'minitial', 'lname', 'privacy_info_link'  ]}),
          ('Profile Images', {'fields': [('profile_sm_image', 'profile_img_small',)\
                , ('profile_med_image', 'profile_img_medium',), ]}),
          ('Email', {'fields': ['email', 'second_email',]}),
          ('Phone', {'fields': ['phone', 'second_phone', ]}),
          ('User Names', {'fields': ['ad_username', 'fas_username',]}),
          ('Visible on Web', {'fields': ['visible', 'visible_profile', 'in_harvard_directory']}),
          ('Physical Address', {'fields': ['room', 'building']}),
          ('Faculty Category', {'fields': ['category']}),
          ('Position Information', {'fields': ['appointment', 'affiliation',  'title','secondary_titles' ,'office', 'secondary_offices',]}),
          ('Research Information', {'fields': ['research_description_title', 'research_description', 'research_summary', 'research_areas']}),
           ('Publications', {'fields': ['publication_html']}),
         
          ('Lab', {'fields': ['primary_lab', 'secondary_labs']}),
          #('Graduate Information', {'fields': ['grad_program', 'grad_year',]}),
          ('Extra', {'fields': ['alt_search_term',]}),

      ]
    
admin.site.register(FacultyMember, FacultyMemberAdmin)

class FacultyCategoryAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display= ('name', 'url_name' )
admin.site.register(FacultyCategory, FacultyCategoryAdmin)

class GalleryImageAdmin(admin.ModelAdmin):
    save_on_top = True
    readonly_fields = ( 'gallery_image', 'gallery_image_small',)
    list_display = ('faculty_member', 'name', 'visible', 'gallery_image', 'gallery_image_small')
    list_filter = ('visible',)
admin.site.register(GalleryImage, GalleryImageAdmin)







