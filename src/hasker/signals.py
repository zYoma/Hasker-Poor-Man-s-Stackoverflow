from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Answer
from django.core.mail import EmailMessage


@receiver(post_save, sender=Answer)
def payment_received(sender, instance, created, **kwargs):
    if created:
        email = EmailMessage(
            'Answer on your question',
            f'See new answer on link {instance.question.id}',
            to=[instance.author.email]
        )
        email.send()
