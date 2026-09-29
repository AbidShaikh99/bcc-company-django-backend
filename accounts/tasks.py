from celery_app.celery import app
from django.conf import settings
from django.core.mail import send_mail


@app.task
def send_user_credentials_email(
    username,
    email,
    temporary_password,
):
    send_mail(
        subject="Your BCC Company Account Credentials",
        message=(
            f"Hello,\n\n"
            f"Your BCC Company account has been created.\n\n"
            f"Username: {username}\n"
            f"Temporary Password: {temporary_password}\n\n"
            f"Please log in and change your password after your first login.\n\n"
            f"Regards,\n"
            f"BCC Company"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return "Credentials email sent successfully"