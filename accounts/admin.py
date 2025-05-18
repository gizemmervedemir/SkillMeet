from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, MatchRequest, Message, MeetingProposal, Rating, Notification


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


class MeetingProposalAdmin(admin.ModelAdmin):
    list_display = ('match', 'location', 'datetime', 'status', 'proposer', 'created_at')
    list_filter = ('status', 'datetime', 'created_at')
    search_fields = ('match__sender__username', 'match__receiver__username', 'location')


class RatingAdmin(admin.ModelAdmin):
    list_display = ('rater', 'rated_user', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('rater__username', 'rated_user__username', 'comment')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MatchRequest, MatchRequestAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MeetingProposal, MeetingProposalAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Notification, NotificationAdmin)