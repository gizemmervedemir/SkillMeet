from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from django.conf import settings
from django.conf.urls.static import static  # Medya dosyaları için

urlpatterns = [
    # Ana sayfa: login sayfasına yönlendirme
    path('', lambda request: redirect('login'), name='root_redirect'),

    # Django admin
    path('admin/', admin.site.urls),

    # Accounts uygulaması URL’leri
    path('accounts/', include('accounts.urls')),
]

# DEBUG modda medya dosyalarının sunulması (örneğin profil fotoğrafı)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)