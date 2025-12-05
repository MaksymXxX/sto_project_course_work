from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceCategoryViewSet, ServiceViewSet, CustomerViewSet,
    AppointmentViewSet, ServiceHistoryViewSet,
    LoyaltyTransactionViewSet, STOInfoViewSet, AdminViewSet,
    BoxViewSet, AuthViewSet, GuestAppointmentViewSet
)

router = DefaultRouter()
router.register(r'service-categories', ServiceCategoryViewSet)
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(
    r'service-history', ServiceHistoryViewSet, basename='service-history')
router.register(
    r'loyalty-transactions',
    LoyaltyTransactionViewSet,
    basename='loyalty-transaction')
router.register(
    r'sto-info', STOInfoViewSet, basename='sto-info')
router.register(r'boxes', BoxViewSet)
router.register(
    r'guest-appointments',
    GuestAppointmentViewSet,
    basename='guest-appointment')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'admin', AdminViewSet, basename='admin')

urlpatterns = [
    path('', include(router.urls)),
]