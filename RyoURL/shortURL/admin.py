from django.contrib import admin
from .models import Url

class UrlAdmin(admin.ModelAdmin):
    list_display = ('orign_url', 'short_string', 'short_url', 'create_date')

admin.site.register(Url, UrlAdmin)