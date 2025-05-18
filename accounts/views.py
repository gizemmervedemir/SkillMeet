from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser, MatchRequest


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

    return render(
        request,
        'accounts/profile.html',
        {
            'form': form,
            'user': request.user,
            'match_requests': match_requests,
            'sent_requests': sent_requests,
        }
    )


@login_required
def send_match_request(request, receiver_id):
    if not request.user.is_approved:
        return HttpResponseForbidden("Only approved users can send match requests.")
    
    receiver = get_object_or_404(CustomUser, id=receiver_id)

    if request.method == 'POST':
        message = request.POST.get('message', '')
        MatchRequest.objects.create(sender=request.user, receiver=receiver, message=message)
        return redirect('profile')

    return render(request, 'accounts/send_match_request.html', {'receiver': receiver})


@login_required
def handle_match_request(request, request_id, action):
    match_request = get_object_or_404(MatchRequest, id=request_id, receiver=request.user)

    if action == 'accept':
        match_request.is_accepted = True
    elif action == 'reject':
        match_request.is_accepted = False
    match_request.save()

    return redirect('profile')