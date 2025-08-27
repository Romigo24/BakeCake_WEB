from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("lk/", TemplateView.as_view(template_name="lk.html")),
    path("lk-order/", TemplateView.as_view(template_name="lk-order.html")),
    path("admin/", admin.site.urls),
    path("api/v1/", include("BakeCake_API.urls")),
]
