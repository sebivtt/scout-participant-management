import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Die App wird immer angelegt. Ist USE_CELERY aus, laufen Aufgaben über
# CELERY_TASK_ALWAYS_EAGER direkt im Webprozess (siehe settings.py).
# Früher wurde hier beim Start die Warteschlange geleert (purge): Das hat bei
# jedem Neustart eines Webprozesses noch nicht versandte Mails verworfen.
app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
