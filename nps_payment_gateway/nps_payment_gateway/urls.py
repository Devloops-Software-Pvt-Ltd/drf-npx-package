from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NpsPaymentViewSet,
    PaymentInstrumentView,
    ProcessIdView,
    NotificationView,
    ServiceChargeView
)

router = DefaultRouter()
router.register(r'npspayment', NpsPaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payment-instruments/', PaymentInstrumentView.as_view(), name='payment-instruments'),
    path('process-id/', ProcessIdView.as_view(), name='process-id'),
    path('notification/', NotificationView.as_view(), name='notification'),
    path('service-charge/', ServiceChargeView.as_view(), name='service-charge'),
]
