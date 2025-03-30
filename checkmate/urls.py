from django.contrib import admin
from django.urls import path, include
from .swagger import CustomSpectacularAPIView, CustomSpectacularSwaggerView, CustomSpectacularRedocView


api_v1_patterns = [
    path('auth/', include('account.urls')),
    path('', include('course_management.urls')),
    path('', include('assignment.urls')),
    path('', include('analytics.urls')),
]

schema_patterns = [
    path("schema/", CustomSpectacularAPIView.as_view(), name="schema"),
    path("", CustomSpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path('redoc/', CustomSpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
] + schema_patterns
