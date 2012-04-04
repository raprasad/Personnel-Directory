from django.contrib import admin
from building.models import Building

class BuildingAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display= ('name','abbrev',  'addr1', 'state', 'zipcode')
    search_fields = ('name', )
admin.site.register(Building, BuildingAdmin)

