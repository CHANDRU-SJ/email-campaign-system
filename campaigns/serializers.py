from rest_framework import serializers
from .models import Campaign, Recipient, DeliveryLog
from datetime import datetime


class RecipientSerializer(serializers.ModelSerializer):
    """Used for adding/viewing recipients."""

    class Meta:
        model = Recipient
        fields = "__all__"
        

class BulkRecipientUploadSerializer(serializers.Serializer):
    """Used to handle CSV/Excel bulk uploads."""
    file = serializers.FileField()

    def validate_file(self, value):
        """Ensure file extension is supported."""
        if not (value.name.endswith(".csv") or value.name.endswith(".xlsx")):
            raise serializers.ValidationError(
                "Unsupported file format. Upload .csv or .xlsx file."
            )
        return value


class CampaignSerializer(serializers.ModelSerializer):
    """Handles creation and listing of campaigns."""

    class Meta:
        model = Campaign
        fields = "__all__"
        read_only_fields = ("sent_count", "failed_count", "total_recipients")
        
    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        # Use existing data for partial updates
        scheduled_time = attrs.get("scheduled_time") or getattr(instance, "scheduled_time", None)
        status = attrs.get("status") or getattr(instance, "status", None)

        # Validation: Scheduled campaign must have a scheduled time
        if status == "scheduled" and not scheduled_time:
            raise serializers.ValidationError("Scheduled campaigns must include a scheduled_time.")

        return attrs
    
    def create(self, validated_data):
        campaign = Campaign.objects.create(**validated_data)
        recipients = Recipient.objects.filter(subscription_status="subscribed")
        campaign.recipients.set(recipients)
        campaign.total_recipients = recipients.count()
        campaign.save(update_fields=["total_recipients"])
        return campaign



class DeliveryLogSerializer(serializers.ModelSerializer):
    """Used for viewing delivery details."""

    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    recipient_name = serializers.CharField(source="recipient.name", read_only=True)

    class Meta:
        model = DeliveryLog
        fields = [
            "id",
            "campaign",
            "campaign_name",
            "recipient",
            "recipient_name",
            "recipient_email",
            "status",
            "failure_reason",
            "sent_at",
            "attempt",
        ]
