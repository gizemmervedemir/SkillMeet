from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from datetime import datetime

from .forms import CustomUserCreationForm, CustomUserUpdateForm, SKILL_CHOICES
from .models import (
    CustomUser, MatchRequest, Message, MeetingProposal,
    Rating, Notification, Venue, PartnerCompany, MatchFeedback
)
from accounts.ml.model_utils import recommend_users_for

# ---------------------------
# AUTHENTICATION
# ---------------------------

def register_view(request):
    skill_options = [{'value': v, 'label': l} for v, l in SKILL_CHOICES]

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    selected_teach = []
    selected_learn = []
    if form.initial.get('skills_can_teach'):
        selected_teach = form.initial['skills_can_teach'].split(',')
    if form.initial.get('skills_want_to_learn'):
        selected_learn = form.initial['skills_want_to_learn'].split(',')

    return render(request, 'accounts/register.html', {
        'form': form,
        'skill_options': skill_options,
        'selected_teach': selected_teach,
        'selected_learn': selected_learn,
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# ---------------------------
# PROFILE
# ---------------------------

@login_required
def profile_view(request):
    skill_options = [{'value': v, 'label': l} for v, l in SKILL_CHOICES]

    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        initial_data = {}
        if request.user.skills_can_teach:
            initial_data['skills_can_teach'] = request.user.skills_can_teach.split(',')
        if request.user.skills_want_to_learn:
            initial_data['skills_want_to_learn'] = request.user.skills_want_to_learn.split(',')
        form = CustomUserUpdateForm(instance=request.user, initial=initial_data)

    selected_teach = initial_data.get('skills_can_teach', [])
    selected_learn = initial_data.get('skills_want_to_learn', [])

    match_requests = MatchRequest.objects.filter(receiver=request.user, is_accepted=None)
    sent_requests = MatchRequest.objects.filter(sender=request.user)

    accepted_matches = MatchRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        is_accepted=True
    ).distinct()

    ratings = request.user.received_ratings.all()
    avg_rating = sum(r.score for r in ratings) / ratings.count() if ratings.exists() else None

    notifications = request.user.notifications.filter(is_read=False)
    notifications.update(is_read=True)

    venues = Venue.objects.filter(is_active=True).order_by('?')[:3]
    partners = PartnerCompany.objects.filter(is_active=True).order_by('?')[:3]

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user,
        'match_requests': match_requests,
        'sent_requests': sent_requests,
        'match_requests_received': accepted_matches,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'notifications': notifications,
        'venues': venues,
        'partner_companies': partners,
        'skill_options': skill_options,
        'selected_teach': selected_teach,
        'selected_learn': selected_learn,
    })

# ---------------------------
# USER PUBLIC PROFILE
# ---------------------------

@login_required
def view_user_profile(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    ratings = target_user.received_ratings.all()
    avg_rating = sum(r.score for r in ratings) / ratings.count() if ratings.exists() else None

    return render(request, 'accounts/view_user_profile.html', {
        'target_user': target_user,
        'ratings': ratings,
        'avg_rating': avg_rating,
    })

# ---------------------------
# NOTIFICATIONS
# ---------------------------

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    for note in notifications:
        if note.related_user:
            username = note.related_user.username
            note.message_prefix = note.message.replace(username, '').strip()
            note.username = username
        else:
            note.message_prefix = note.message
            note.username = None
    return render(request, 'accounts/notification_list.html', {
        'notifications': notifications
    })

# ---------------------------
# PARTNER VENUES
# ---------------------------

@login_required
def partner_venues_view(request):
    partners = PartnerCompany.objects.filter(is_active=True).order_by('name')
    return render(request, 'accounts/partner_venues.html', {
        'partners': partners
    })

@login_required
def apply_discount(request, partner_id):
    partner = get_object_or_404(PartnerCompany, id=partner_id, is_active=True)

    if not request.user.can_apply_for_discount():
        messages.warning(request, "You must be at least Blue Belt to apply for discounts.")
        return redirect('partner_venues')

    messages.success(request, f"You successfully applied for {partner.name}'s discount. They will contact you soon.")
    return redirect('partner_venues')

# ---------------------------
# MATCH SYSTEM
# ---------------------------

@login_required
def send_match_request(request, receiver_id):
    receiver = get_object_or_404(CustomUser, id=receiver_id)

    if request.method == 'POST':
        message = request.POST.get('message', '')
        MatchRequest.objects.create(sender=request.user, receiver=receiver, message=message)
        Notification.objects.create(
            user=receiver,
            message=f"You received a match request from {request.user.username}",
            related_user=request.user
        )
        return redirect('suggestions')

    return render(request, 'accounts/send_match_request.html', {'receiver': receiver})

@login_required
def handle_match_request(request, request_id, action):
    match_request = get_object_or_404(MatchRequest, id=request_id, receiver=request.user)

    if action == 'accept':
        match_request.is_accepted = True
        Notification.objects.create(
            user=match_request.sender,
            message=f"Your match request was accepted by {request.user.username}",
            related_user=request.user
        )
    elif action == 'reject':
        match_request.is_accepted = False

    match_request.save()
    return redirect('profile')

# ---------------------------
# CHAT
# ---------------------------

@login_required
def conversation_view(request, other_id):
    other = get_object_or_404(CustomUser, id=other_id)

    matched = MatchRequest.objects.filter(
        Q(sender=request.user, receiver=other, is_accepted=True) |
        Q(sender=other, receiver=request.user, is_accepted=True)
    ).exists()

    if not matched:
        return HttpResponseForbidden("You must be matched to chat.")

    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=other) |
        Q(sender=other, receiver=request.user)
    ).order_by('timestamp')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(sender=request.user, receiver=other, text=text)
            Notification.objects.create(
                user=other,
                message=f"New message from {request.user.username}",
                related_user=request.user
            )
        return redirect('conversation', other_id=other.id)

    return render(request, 'accounts/conversation.html', {
        'other': other,
        'messages': messages_qs,
    })

# ---------------------------
# MEETINGS
# ---------------------------

@login_required
def propose_meeting(request, match_id):
    match = get_object_or_404(MatchRequest, id=match_id, is_accepted=True)

    if match.sender != request.user and match.receiver != request.user:
        return HttpResponseForbidden("You’re not part of this match.")

    class Option:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    meeting_options = [
        Option(0, "Google Meet (Online)"),
        Option(1, "Face to Face")
    ]

    if request.method == 'POST':
        location_id = request.POST.get('location')
        datetime_str = request.POST.get('datetime')
        message = request.POST.get('message', '')

        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')

        if location_id == '0':
            location_name = "Google Meet (Online)"
        else:
            location_name = "Face to Face"

        MeetingProposal.objects.create(
            match=match,
            proposer=request.user,
            location=location_name,
            datetime=dt,
            message=message
        )
        return redirect('profile')

    return render(request, 'accounts/propose_meeting.html', {
        'match': match,
        'venues': meeting_options,
    })

@login_required
def handle_meeting_response(request, proposal_id, action):
    proposal = get_object_or_404(MeetingProposal, id=proposal_id)

    if proposal.match.receiver != request.user and proposal.match.sender != request.user:
        return HttpResponseForbidden("You can't respond to this meeting.")

    if action == 'accept':
        proposal.status = 'accepted'
    elif action == 'reject':
        proposal.status = 'rejected'

    proposal.save()
    return redirect('profile')

@login_required
def list_meetings(request):
    proposals = MeetingProposal.objects.filter(
        Q(match__sender=request.user) |
        Q(match__receiver=request.user)
    ).order_by('-created_at')

    return render(request, 'accounts/meeting_list.html', {'proposals': proposals})

# ---------------------------
# RATING + FEEDBACK
# ---------------------------

@login_required
def rate_user(request, user_id):
    target = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        score = int(request.POST.get('score'))
        comment = request.POST.get('comment', '')

        if score < 1 or score > 5:
            return HttpResponseForbidden("Invalid score.")

        Rating.objects.create(
            rater=request.user,
            rated_user=target,
            score=score,
            comment=comment
        )

        MatchFeedback.objects.create(
            sender=request.user,
            receiver=target,
            rating=score,
            comment=comment
        )

        Notification.objects.create(
            user=target,
            message=f"You received a new rating from {request.user.username}",
            related_user=request.user
        )

        target.update_dojo_level()
        return redirect('profile')

    return render(request, 'accounts/rate_user.html', {'target': target})

# ---------------------------
# SUGGESTIONS (ML BASED)
# ---------------------------

@login_required
def suggestions_view(request):
    recommended = recommend_users_for(request.user.id, top_n=5)
    users = [(CustomUser.objects.get(id=rec['id']), rec['score']) for rec in recommended]

    return render(request, 'accounts/suggestions.html', {
        'suggestions': users
    })

# ---------------------------
# CATEGORY FILTERS
# ---------------------------

@login_required
def category_view(request, category):
    users = CustomUser.objects.exclude(id=request.user.id)
    filtered_users = []

    for user in users:
        skills = (user.skills_can_teach or "") + " " + (user.skills_want_to_learn or "")
        if category.lower() == "sports" and any(k in skills.lower() for k in ["sport", "basketball", "tennis", "fitness"]):
            filtered_users.append(user)
        elif category.lower() == "art" and any(k in skills.lower() for k in ["art", "painting", "drawing", "sculpture"]):
            filtered_users.append(user)
        elif category.lower() == "language" and any(k in skills.lower() for k in ["language", "english", "turkish", "french", "german"]):
            filtered_users.append(user)
        elif category.lower() == "music" and any(k in skills.lower() for k in ["music", "guitar", "piano", "violin", "drums"]):
            filtered_users.append(user)
        elif category.lower() == "others":
            filtered_users.append(user)

    return render(request, 'accounts/category.html', {
        'category': category.title(),
        'users': filtered_users,
    })