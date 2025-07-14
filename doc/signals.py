from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def refresh_fts_index_after_migrate(sender, **kwargs):
    if sender.name != "doc":
        return

    try:
        call_command("refresh_text_index")
    except Exception as e:
        print(f"Exception while executing refresh_text_index: {e}")
