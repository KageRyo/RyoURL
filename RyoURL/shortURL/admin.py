from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Url, User 

class UrlAdmin(admin.ModelAdmin):
    list_display = ('origin_url', 'short_string', 'short_url', 'create_date', 'expire_date', 'visit_count', 'user')

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type')
    list_filter = UserAdmin.list_filter + ('user_type',)
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type',)}),
    )

admin.site.register(Url, UrlAdmin)
admin.site.register(User, CustomUserAdmin)