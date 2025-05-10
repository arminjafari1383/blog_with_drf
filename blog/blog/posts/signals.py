from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Category

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    default_categories = ['آموزش', 'فناوری', 'سلامت', 'سرگرمی']

    for name in default_categories:
        Category.objects.get_or_create(name=name)
