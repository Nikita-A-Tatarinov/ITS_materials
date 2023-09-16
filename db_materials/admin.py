from django.contrib import admin

from db_materials.models import Material, MaterialElement

admin.site.site_url = "db_materials:view_site"
admin.site.register(Material)
admin.site.register(MaterialElement)
