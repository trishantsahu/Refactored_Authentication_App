from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def feedback_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        send_mail(
            subject=f"Feedback from {name}",
            message=description,
            # Was settings.EMAIL_HOST_USER, which is unset when using the
            # console email backend (dev/test) and would raise an error.
            # DEFAULT_FROM_EMAIL is always defined.
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )
        return JsonResponse({"message": "Feedback sent successfully!"})
    return render(request, "UserAuthentication/feedback.html")
