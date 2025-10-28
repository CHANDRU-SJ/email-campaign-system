from django.db import models


class Recipient(models.Model):
    """
    Represents a single email recipient (subscriber or unsubscribed user).
    Used for targeting email campaigns.
    """
    
    SUBSCRIPTION_CHOICES = [
        ("subscribed", "Subscribed"),
        ("unsubscribed", "Unsubscribed"),
    ]
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    subscription_status = models.CharField(
        max_length=20, choices=SUBSCRIPTION_CHOICES, default="subscribed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recipients'
        indexes = [models.Index(fields=["email"])]

    def __str__(self):
        return self.email

    
class Campaign(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    # Email content, stored as plain text or HTML. Can include template variables like {{ name }}.

    recipients = models.ManyToManyField(
        Recipient, blank=True, related_name="campaigns"
    )
    
    scheduled_time = models.DateTimeField(null=True, blank=True)
    # Determines when the campaign is set to run. Nullable to allow drafts.

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="draft")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_recipients = models.IntegerField(default=0)
    # Cached total count of recipients for quick dashboard summary.

    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    # Maintain sent/failed counts in real-time to avoid expensive log aggregation queries.

    class Meta:
        db_table = 'campaigns'
    
    def __str__(self):
        return self.name


class DeliveryLog(models.Model):
    STATUS_CHOICES = [
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="logs")
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name="delivery_logs")
    recipient_email = models.EmailField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    failure_reason = models.TextField(blank=True, null=True)
    # Stores provider or SMTP failure details for analysis.
    sent_at = models.DateTimeField(null=True, blank=True)
    # Timestamp when the message was sent successfully.
    attempt = models.IntegerField(default=0)
    # Retry tracking. Helps avoid infinite resend loops and identify repeated failures.

    class Meta:
        db_table = "delivery_logs"
        indexes = [models.Index(fields=["campaign", "recipient_email"])]

    def __str__(self):
        return f"{self.campaign.name} -> {self.recipient_email} ({self.status})"