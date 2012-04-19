from person.models import SecondaryTitle
<<<<<<< HEAD
from faculty.models import *
=======
from faculty.models import FacultyCategory, ResearchArea, FacultyMember, FacultyLink, GalleryImage
>>>>>>> updated model, renaming url_name to slug
#from person.admin import PersonAdmin
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
    list_display= ('name', 'slug' )    
<<<<<<< HEAD
    search_fields = ('name', )
=======
>>>>>>> updated model, renaming url_name to slug
admin.site.register(ResearchArea, ResearchAreaAdmin)

class FacultyLinkAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name', )
    
    list_display= ('faculty_member', 'name', 'url',)   
admin.site.register(FacultyLink, FacultyLinkAdmin)


class SecondaryTitleInline(admin.TabularInline):
  model = SecondaryTitle
  extra = 0

class FacultyMemberAdmin(admin.ModelAdmin):
    inlines = [SecondaryTitleInline, FacultyLink_Inline, GalleryImage_Inline]    # FacultyPublicationInline]
    save_on_top = True
    readonly_fields = ['privacy_info_link', 'profile_img_small', 'profile_img_medium', 'date_added', 'date_modified', 'id_hash']
    list_display = ('lname', 'fname', 'minitial', 'profile_img_small', 'profile_img_medium', 'email', 'phone','category', 'affiliation', 'appointment','title', 'visible')
    search_fields = ('lname','fname',  'email', 'second_email' )
    list_filter = ( 'visible','visible_profile', 'category', 'research_areas','affiliation', )
<<<<<<< HEAD
    filter_horizontal = ( 'secondary_labs', 'research_areas', 'secondary_offices', 'tags',)
    filter_vertical = ('secondary_titles', )
=======
    filter_horizontal = ( 'secondary_labs', 'research_areas','secondary_offices',)
    filter_vertical = ( )
>>>>>>> updated model, renaming url_name to slug
    #inlines = [ResearchInformationInline, ]
    
    # list_editable = ('email','phone','fname',)# 'lname',)
    #positions = ('labs',)
    fieldsets = [
          ('Name',               {'fields': ['fname', 'minitial', 'lname', 'privacy_info_link'  ]}),
          ('Profile Images', {'fields': [('profile_sm_image', 'profile_img_small',)\
                , ('profile_med_image', 'profile_img_medium',), ]}),
          ('Email', {'fields': ['email', 'second_email',]}),
          ('Phone', {'fields': ['phone', 'second_phone', ]}),
<<<<<<< HEAD
          ('User Names', {'fields': ['ad_username', 'fas_username',]}),
          ('Visible on Web', {'fields': ['visible', 'visible_profile', ]}),
          ('Physical Address', {'fields': ['room', 'building']}),
          ('Faculty Category', {'fields': ['category']}),
          ('Position Information', {'fields': ['appointment', 'affiliation',  'title','secondary_titles' ,]}),
          ('Research Information', {'fields': ['research_description_title', 'research_description', 'research_summary', 'research_areas']}),
           ('Publications', {'fields': ['publication_html']}),
         
          ('Lab', {'fields': ['primary_lab', 'secondary_labs']}),
          ('Offices', {'fields': ['office', 'secondary_offices']}),
=======
          #('User Names', {'fields': ['ad_username', 'fas_username',]}),
          ('Visible on Web', {'fields': ['visible', 'visible_profile', ]}),
          ('Physical Address', {'fields': ['room', 'building']}),
          ('Faculty Category', {'fields': ['category']}),
          ('Position Information', {'fields': ['appointment', 'affiliation',  'title' ,]}),
          ('Lab', {'fields': ['primary_lab', 'secondary_labs']}),
          ('Office', {'fields': ('office', 'secondary_offices',)}),
          ('Research Information', {'fields': ['research_description_title', 'research_description', 'research_summary', 'research_areas']}),
           ('Publications', {'fields': ['publication_html']}),
         
>>>>>>> updated model, renaming url_name to slug
          #('Graduate Information', {'fields': ['grad_program', 'grad_year',]}),
          ('Extra', {'fields': ['alt_search_term',]}),
          ('Tags', {'fields': ['tags',]}),
          ('Internal Info', {'fields': ['date_added', 'date_modified', 'id_hash']}),

      ]
    
admin.site.register(FacultyMember, FacultyMemberAdmin)

class FacultyCategoryAdmin(admin.ModelAdmin):
    save_on_top = True
<<<<<<< HEAD
    list_display= ('name', 'sort_order', 'slug' )
=======
    list_display= ('name', 'slug' )
>>>>>>> updated model, renaming url_name to slug
admin.site.register(FacultyCategory, FacultyCategoryAdmin)

class GalleryImageAdmin(admin.ModelAdmin):
    save_on_top = True
    readonly_fields = ( 'gallery_image', 'gallery_image_small',)
    list_display = ('faculty_member', 'name', 'visible', 'gallery_image', 'gallery_image_small')
    list_filter = ('visible',)
admin.site.register(GalleryImage, GalleryImageAdmin)







