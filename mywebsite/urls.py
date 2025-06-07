from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('panda/', admin.site.urls),
    path('', include('core.urls')),           # core uygulamasını dahil et
    path('tinymce/', include('tinymce.urls')),
    path('captcha/', include('captcha.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)