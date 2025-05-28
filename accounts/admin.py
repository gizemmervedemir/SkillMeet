from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django import forms
from django.contrib import messages

from .models import (
    CustomUser, MatchRequest, Message, MeetingProposal,
    Rating, Notification, PartnerCompany, Venue, MarketingCampaign
)

# ✅ Admin actions for approving users
@admin.action(description="✅ Approve selected users")
def approve_users(modeladmin, request, queryset):
    queryset.update(is_approved=True)

@admin.action(description="🚫 Unapprove selected users")
def unapprove_users(modeladmin, request, queryset):
    queryset.update(is_approved=False)

# 👤 Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_approved', 'dojo_level', 'city')
    list_filter = ('is_approved', 'dojo_level', 'city')
    readonly_fields = ('profile_image_preview',)
    actions = [approve_users, unapprove_users]

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
                'profile_image',
                'profile_image_preview',
            )
        }),
    )

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 50%;" />',
                obj.profile_image.url
            )
        return "(No image)"
    profile_image_preview.short_description = "Profile Preview"

    def has_delete_permission(self, request, obj=None):
        return True


# 📬 Match Request Admin
class MatchRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('sender__username', 'receiver__username')


# 💌 Message Admin
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'text')
    list_filter = ('timestamp',)


# 📅 Meeting Proposal Admin
class MeetingProposalAdmin(admin.ModelAdmin):
    list_display = ('match', 'location', 'datetime', 'status', 'proposer', 'created_at')
    list_filter = ('status', 'datetime', 'created_at')
    search_fields = ('match__sender__username', 'match__receiver__username', 'location')


# 🌟 Rating Admin
class RatingAdmin(admin.ModelAdmin):
    list_display = ('rater', 'rated_user', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('rater__username', 'rated_user__username', 'comment')


# 📢 Broadcast Notification Form
class NotificationBroadcastForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), label="Broadcast Message")


# 🔔 Notification Admin with Broadcast Button
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    actions = ['send_broadcast']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('broadcast/', self.admin_site.admin_view(self.broadcast_view), name='notification-broadcast'),
        ]
        return custom_urls + urls

    def send_broadcast(self, request, queryset):
        # Redirect to the broadcast form view instead of acting on queryset
        return redirect('admin:notification-broadcast')

    def broadcast_view(self, request):
        if request.method == 'POST':
            form = NotificationBroadcastForm(request.POST)
            if form.is_valid():
                message_text = form.cleaned_data['message']
                users = CustomUser.objects.all()
                notifications = [Notification(user=user, message=message_text) for user in users]
                Notification.objects.bulk_create(notifications)
                self.message_user(request, "✅ Broadcast sent to all users.", messages.SUCCESS)
                return redirect('..')
        else:
            form = NotificationBroadcastForm()

        context = {
            'form': form,
            'title': "📢 Send Notification to All Users",
        }
        return render(request, 'admin/broadcast_notification.html', context)

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        broadcast_url = reverse('admin:notification-broadcast')
        extra_context['broadcast_button'] = format_html(
            '<a class="btn btn-success" style="margin-bottom: 10px;" href="{}">📢 Send Broadcast</a>', broadcast_url
        )
        return super().changelist_view(request, extra_context=extra_context)


# 🏢 Partner Company Admin
class PartnerCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'website', 'is_active', 'type', 'created_at', 'logo_preview')
    list_filter = ('is_active', 'type', 'created_at')
    search_fields = ('name', 'contact_email')
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: contain;" />',
                obj.logo.url
            )
        return "(No logo)"
    logo_preview.short_description = "Logo Preview"


# 🏟️ Venue Admin
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'capacity', 'available_for_teaching', 'type')
    list_filter = ('city', 'available_for_teaching', 'type')
    search_fields = ('name', 'city')


# 📣 Marketing Campaign Admin
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'start_date', 'end_date', 'budget', 'is_active')
    list_filter = ('platform', 'is_active', 'start_date')
    search_fields = ('title', 'description')


# ✅ Register all models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MatchRequest, MatchRequestAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MeetingProposal, MeetingProposalAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(PartnerCompany, PartnerCompanyAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(MarketingCampaign, MarketingCampaignAdmin)