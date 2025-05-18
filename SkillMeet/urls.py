from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login'), name='root_redirect'),  # Root URL yönlendirmesi
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]