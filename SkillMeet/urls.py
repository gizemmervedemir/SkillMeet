from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from django.conf import settings
from django.conf.urls.static import static  # Medya dosyaları için

urlpatterns = [
    path('', lambda request: redirect('login'), name='root_redirect'),  # Ana sayfa -> login'e yönlendir
    path('admin/', admin.site.urls),                                     # Django admin paneli
    path('accounts/', include('accounts.urls')),                         # Accounts app url'leri
]

# DEBUG modda media dosyalarını sunmak için
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)