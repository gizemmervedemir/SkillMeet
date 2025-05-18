from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, MatchRequest, Message


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_approved', 'dojo_level')
    list_filter = ('is_approved', 'dojo_level', 'city')
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': (
                'bio',
                'skills_can_teach',
                'skills_want_to_learn',
                'city',
                'is_approved',
                'dojo_level',
            )
        }),
    )


class MatchRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('sender__username', 'receiver__username')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'text')
    list_filter = ('timestamp',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MatchRequest, MatchRequestAdmin)
admin.site.register(Message, MessageAdmin)