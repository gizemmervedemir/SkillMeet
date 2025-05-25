from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, MatchRequest, Message, MeetingProposal,
    Rating, Notification, PartnerCompany, Venue, MarketingCampaign
)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_approved', 'dojo_level', 'city')
    list_filter = ('is_approved', 'dojo_level', 'city')
    readonly_fields = ('profile_picture_preview',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': (
                'bio',
                'skills_can_teach',
                'skills_want_to_learn',
                'city',
                'category',
                'is_approved',
                'dojo_level',
                'profile_picture',
                'profile_picture_preview',
            )
        }),
    )

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return f'<img src="{obj.profile_picture.url}" width="80" height="80" style="object-fit: cover; border-radius: 50%;" />'
        return "(No image)"
    profile_picture_preview.allow_tags = True
    profile_picture_preview.short_description = "Preview"


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


class PartnerCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'website', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'contact_email')


class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'capacity', 'available_for_teaching')
    list_filter = ('city', 'available_for_teaching')
    search_fields = ('name', 'city')


class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'start_date', 'end_date', 'budget', 'is_active')
    list_filter = ('platform', 'is_active', 'start_date')
    search_fields = ('title', 'description')


# Register models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MatchRequest, MatchRequestAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MeetingProposal, MeetingProposalAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(PartnerCompany, PartnerCompanyAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(MarketingCampaign, MarketingCampaignAdmin)