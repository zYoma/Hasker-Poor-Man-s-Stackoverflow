from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from config import settings

from .views import page_not_found, server_error


handler404 = 'config.views.page_not_found'  # noqa
handler500 = 'config.views.server_error'  # noqa
schema_view = get_schema_view(
    openapi.Info(
        title="Hasker API",
        default_version='v1',
        description="Test description",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('404/', page_not_found),
    path('500/', server_error),
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')),
    path('', include('hasker.urls')),
    path('api/v1/', include('api.urls')),
]
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
        re_path(r'^docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
