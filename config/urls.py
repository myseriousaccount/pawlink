from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('animals/', include('animals.urls')),
    path('adoptions/', include('adoptions.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('shelters/', include('shelters.urls')),
    path('support/', include('support.urls')),
]

# for local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, )
