from django.shortcuts import render

from campaigns.serializers import CampaignSerializer
from ..models import Campaign

def campaign_form(request):
    if request.method == "POST":
        name = request.POST.get("name")
        subject = request.POST.get("subject")
        content = request.POST.get("content")
        scheduled_time = request.POST.get("scheduled_time")

        if name and subject and content:
            serializer = CampaignSerializer(data={
                "name": name,
                "subject": subject,
                "body": content,
                "scheduled_time": scheduled_time or None
                })
            
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except Exception as e:
                return render(request, "create_campaign.html", {"error": str(e)})
            return render(request, "create_campaign.html", {"message": "Campaign created successfully!"})
        else:
            return render(request, "create_campaign.html", {"error": "All fields are required."})

    return render(request, "create_campaign.html")
