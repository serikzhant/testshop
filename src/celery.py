import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
app = Celery('src')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'send-mail-every-day': {
#         'task': 'payment.tasks.send_mail',
#         'schedule': crontab(),
#     },
# }
