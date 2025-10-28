from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper
from ..models import Campaign, DeliveryLog, Recipient
from ..serializers import CampaignSerializer, DeliveryLogSerializer, RecipientSerializer, BulkRecipientUploadSerializer
from ..utils.file_importer import import_recipients_from_file
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RecipientViewSet(viewsets.ModelViewSet):
    queryset = Recipient.objects.all().order_by("-created_at")
    serializer_class = RecipientSerializer
    
    @swagger_auto_schema(
        method="post",
        operation_summary="Bulk upload recipients",
        operation_description="""
        Upload a CSV or Excel (.xlsx) file containing recipient data.
        The file will be validated using the serializer and processed.
        """,
        request_body=BulkRecipientUploadSerializer,
        consumes=["multipart/form-data"],
        responses={
            200: openapi.Response("File uploaded successfully"),
            400: openapi.Response("Invalid file or data format"),
        },
    )
    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request):
        """
        Upload CSV/Excel file containing recipient data.
        Validates and inserts efficiently.
        """
        serializer = BulkRecipientUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]
        try:
            result = import_recipients_from_file(file)
            return Response(
                {
                    "message": "Bulk upload completed",
                    "summary": result,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all().order_by("-created_at")
    serializer_class = CampaignSerializer
    
    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        # Overall summary
        summary_data = Campaign.objects.aggregate(
            total_campaigns=Count("id"),
            total_emails_sent=Sum("sent_count"),
            total_failed=Sum("failed_count")
        )

        # Per-campaign details
        campaigns = Campaign.objects.annotate(
            success_rate=ExpressionWrapper(
                (F("sent_count") - F("failed_count")) * 100.0 / F("sent_count"),
                output_field=FloatField()
            )
        ).values("id", "name", "sent_count", "failed_count", "success_rate")

        # Build response
        data = {
            "summary": summary_data,
            "campaigns": list(campaigns)
        }
        return Response(data)


class DeliveryLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DeliveryLog.objects.select_related("campaign", "recipient")
    serializer_class = DeliveryLogSerializer
    
