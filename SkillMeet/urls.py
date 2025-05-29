from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from django.conf import settings
from django.conf.urls.static import static  # Medya dosyaları için

urlpatterns = [
    path('', lambda request: redirect('login'), name='root_redirect'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]

# Opsiyonel: sadece local testlerde kullanılır
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)