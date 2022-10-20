from django.contrib import admin
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from django.urls import path, include
from config import settings

from .views import page_not_found, server_error

handler404 = 'config.views.page_not_found'  # noqa
handler500 = 'config.views.server_error'  # noqa


urlpatterns = [
    path('404/', page_not_found),
    path('500/', server_error),
    path('admin/', admin.site.urls),
    path('user/',  include('users.urls')),
    path('',  include('hasker.urls')),
]
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL,
    #                       document_root=settings.STATIC_ROOT)
