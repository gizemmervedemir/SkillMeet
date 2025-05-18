from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Match System
    path('match/<int:receiver_id>/', views.send_match_request, name='send_match_request'),
    path('match/<int:request_id>/<str:action>/', views.handle_match_request, name='handle_match_request'),

    # Chat
    path('chat/<int:other_id>/', views.conversation_view, name='conversation'),

    # Meetings
    path('meeting/propose/<int:match_id>/', views.propose_meeting, name='propose_meeting'),
    path('meeting/respond/<int:proposal_id>/<str:action>/', views.handle_meeting_response, name='handle_meeting_response'),
    path('meetings/', views.list_meetings, name='meeting_list'),

    # Ratings
    path('rate/<int:user_id>/', views.rate_user, name='rate_user'),

    # Smart Suggestions
    path('suggestions/', views.suggestions_view, name='suggestions'),
]