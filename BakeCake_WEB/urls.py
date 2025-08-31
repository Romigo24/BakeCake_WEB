from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from BakeCake_API import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("lk/", TemplateView.as_view(template_name="lk.html")),
    path("lk-order/", TemplateView.as_view(template_name="lk-order.html")),
    path("admin/", admin.site.urls),
    path("api/", include("BakeCake_API.urls")),
    path('order/<int:order_id>/pay/', views.create_payment_view, name='create_payment'),
    path('order/<int:order_id>/payment/success/', views.payment_success, name='payment_success'),
    path('webhook/yookassa/', views.yookassa_webhook, name='yookassa_webhook'),
]
