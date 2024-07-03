# signals.py
import uuid
from django.dispatch import receiver
from djoser.signals import user_registered
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@receiver(user_registered)
def user_registered_handler(user, request, **kwargs):
    custom_user, created = CustomUser.objects.get_or_create(
        username=user.username,
        defaults={
            'email': user.email,
            'password': user.password,
            'is_superuser': user.is_superuser,
            'unique_uuid_user': uuid.uuid4()
        }
    )
    if created:
        custom_user.save()
