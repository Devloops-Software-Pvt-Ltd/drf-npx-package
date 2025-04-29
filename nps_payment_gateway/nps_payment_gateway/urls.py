from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NpsPaymentViewSet

router = DefaultRouter()
router.register(r'npspayment', NpsPaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
