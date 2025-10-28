# campaigns/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DeliveryLog


@receiver(post_save, sender=DeliveryLog)
def update_campaign_counters(sender, instance, **kwargs):
    """
    Automatically update Campaign counters when DeliveryLog changes.
    """
    campaign = instance.campaign

    sent = campaign.logs.filter(status="sent").count()
    failed = campaign.logs.filter(status="failed").count()
    total = campaign.recipients.count()

    campaign.sent_count = sent
    campaign.failed_count = failed
    campaign.total_recipients = total
    campaign.save(update_fields=["sent_count", "failed_count", "total_recipients"])
