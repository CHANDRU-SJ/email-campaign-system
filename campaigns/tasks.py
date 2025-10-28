from celery import shared_task
from django.template import Template, Context
from campaigns.models import Campaign, Recipient, DeliveryLog
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import csv, io, os
from datetime import datetime, timezone


@shared_task
def schedule_pending_campaigns():
    print("Checking for pending campaigns to schedule...")
    now = datetime.now()
    campaigns = Campaign.objects.filter(status="scheduled", scheduled_time__lte=now)
    print("Scheduling campaigns:", campaigns)
    for campaign in campaigns:
        execute_campaign.delay(campaign.id)

@shared_task
def execute_campaign(campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    recipients = campaign.recipients.filter(subscription_status="subscribed")

    print(f"Executing campaign {campaign.id} to {recipients.count()} recipients.")
    
    campaign.status = "in_progress"
    campaign.save(update_fields=["status"])

    sent_count = 0
    failed_count = 0

    for recipient in recipients:
        try:
            
            body_template = Template(campaign.body)
            context = Context({
                "name": recipient.name or "Subscriber",
                "email": recipient.email,
            })
            personalized_body = body_template.render(context)
            
            send_mail(
                subject=campaign.subject,
                message=personalized_body,
                from_email=os.getenv("FROM_EMAIL", "no-reply@company.com"),
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            DeliveryLog.objects.create(
                campaign=campaign,
                recipient=recipient,
                status="sent",
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send email to {recipient.email}: {e}")
            DeliveryLog.objects.create(
                campaign=campaign,
                recipient=recipient,
                status="failed",
                failure_reason=str(e),
            )
            failed_count += 1

    campaign.sent_count = sent_count
    campaign.failed_count = failed_count
    campaign.status = "completed"
    campaign.save(update_fields=["sent_count", "failed_count", "status"])
    
    send_campaign_report.delay(campaign.id)

@shared_task
def send_campaign_report(campaign_id):

    campaign = Campaign.objects.get(id=campaign_id)
    logs = campaign.logs.all()
    print(logs)

    csv_file = io.StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(["Recipient", "Status", "Failure Reason"])
    for log in logs:
        writer.writerow([log.recipient.email, log.status, log.failure_reason or ""])

    email = EmailMessage(
        subject=f"Campaign Report: {campaign.name}",
        body="Please find attached the campaign delivery report.",
        to=[os.getenv("ADMIN_EMAIL", "admin@company.com")],
    )
    email.attach(f"{campaign.name}_report.csv", csv_file.getvalue(), "text/csv")
    email.send()
