from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from survey.models import Submission


User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Submission.objects.create(user=instance)
    instance.submission.save()
