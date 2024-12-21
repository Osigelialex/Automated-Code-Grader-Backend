from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView, SpectacularRedocView


class CustomSpectacularSwaggerView(SpectacularSwaggerView):
    authentication_classes = []
    permission_classes = []


class CustomSpectacularAPIView(SpectacularAPIView):
    authentication_classes = []
    permission_classes = []


class CustomSpectacularRedocView(SpectacularRedocView):
    authentication_classes = []
    permission_classes = []
