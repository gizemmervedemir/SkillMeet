from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from datetime import datetime

from .forms import CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser, MatchRequest, Message, MeetingProposal, Rating, Notification


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


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


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    match_requests = MatchRequest.objects.filter(receiver=request.user, is_accepted=None)
    sent_requests = MatchRequest.objects.filter(sender=request.user)
    received_matches = MatchRequest.objects.filter(receiver=request.user, is_accepted=True)

    ratings = request.user.received_ratings.all()
    avg_rating = (
        sum(r.score for r in ratings) / ratings.count()
        if ratings.exists() else None
    )

    notifications = request.user.notifications.filter(is_read=False)
    notifications.update(is_read=True)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user,
        'match_requests': match_requests,
        'sent_requests': sent_requests,
        'match_requests_received': received_matches,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'notifications': notifications,
    })


@login_required
def send_match_request(request, receiver_id):
    if not request.user.is_approved:
        return HttpResponseForbidden("Only approved users can send match requests.")

    receiver = get_object_or_404(CustomUser, id=receiver_id)

    if request.method == 'POST':
        message = request.POST.get('message', '')
        MatchRequest.objects.create(sender=request.user, receiver=receiver, message=message)

        Notification.objects.create(
            user=receiver,
            message=f"You received a match request from {request.user.username}"
        )

        return redirect('profile')

    return render(request, 'accounts/send_match_request.html', {'receiver': receiver})


@login_required
def handle_match_request(request, request_id, action):
    match_request = get_object_or_404(MatchRequest, id=request_id, receiver=request.user)

    if action == 'accept':
        match_request.is_accepted = True

        Notification.objects.create(
            user=match_request.sender,
            message=f"Your match request was accepted by {request.user.username}"
        )

    elif action == 'reject':
        match_request.is_accepted = False

    match_request.save()
    return redirect('profile')


@login_required
def conversation_view(request, other_id):
    other = get_object_or_404(CustomUser, id=other_id)

    matched = MatchRequest.objects.filter(
        Q(sender=request.user, receiver=other, is_accepted=True) |
        Q(sender=other, receiver=request.user, is_accepted=True)
    ).exists()

    if not matched:
        return HttpResponseForbidden("You must be matched to chat.")

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other) |
        Q(sender=other, receiver=request.user)
    ).order_by('timestamp')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(sender=request.user, receiver=other, text=text)

            Notification.objects.create(
                user=other,
                message=f"New message from {request.user.username}"
            )

        return redirect('conversation', other_id=other.id)

    return render(request, 'accounts/conversation.html', {
        'other': other,
        'messages': messages,
    })


@login_required
def propose_meeting(request, match_id):
    match = get_object_or_404(MatchRequest, id=match_id, is_accepted=True)

    if match.sender != request.user and match.receiver != request.user:
        return HttpResponseForbidden("You’re not part of this match.")

    if request.method == 'POST':
        location = request.POST.get('location')
        datetime_str = request.POST.get('datetime')
        message = request.POST.get('message', '')

        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')

        MeetingProposal.objects.create(
            match=match,
            proposer=request.user,
            location=location,
            datetime=dt,
            message=message
        )
        return redirect('profile')

    return render(request, 'accounts/propose_meeting.html', {'match': match})


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

        Notification.objects.create(
            user=target,
            message=f"You received a new rating from {request.user.username}"
        )

        target.update_dojo_level()
        return redirect('profile')

    return render(request, 'accounts/rate_user.html', {'target': target})