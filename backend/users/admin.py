from django.contrib import admin

from .models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name',)
    search_fields = ('username', 'email')
    list_filter = ('username', 'email',)


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    list_filter = ('author',)
    search_fields = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
