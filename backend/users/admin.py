from django.contrib import admin

from .models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name',)


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
