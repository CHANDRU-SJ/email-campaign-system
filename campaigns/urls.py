from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.views import CampaignViewSet, RecipientViewSet, DeliveryLogViewSet
from .views.campaign_creation import campaign_form

router = DefaultRouter()
router.register(r"campaigns", CampaignViewSet, basename="campaign")
router.register(r"recipients", RecipientViewSet, basename="recipient")
router.register(r"delivery-logs", DeliveryLogViewSet, basename="deliverylog")

urlpatterns = [
    # API routes from DRF router
    path("", include(router.urls)),

    # Campaign HTML form page
    path("campaigns/create/form", campaign_form, name="campaign_form"),
]
