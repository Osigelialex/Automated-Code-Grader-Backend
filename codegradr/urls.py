from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularSwaggerView,
    SpectacularAPIView,
    SpectacularRedocView
)

api_v1_patterns = [
    path('account/', include('account.urls')),
    path('course/', include('course_management.urls')),
    path('', include('assignment.urls')),
]

schema_patterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
] + schema_patterns
