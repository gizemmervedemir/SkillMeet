from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Match request routes
    path('match/<int:receiver_id>/', views.send_match_request, name='send_match_request'),
    path('match/<int:request_id>/<str:action>/', views.handle_match_request, name='handle_match_request'),
]