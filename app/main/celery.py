import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'totalcoin-task': {
        'task': 'parsing.tasks.totalcoin',
        'schedule': 30,
    },
    'kucoin-task': {
        'task': 'parsing.tasks.kucoin',
        'schedule': 30,
    },

    'count-two-actions-task': {
        'task': 'count.tasks.count_in_two_actions',
        'schedule': 30,
    },
    'count-three-actions-task': {
        'task': 'count.tasks.count_in_three_actions',
        'schedule': 30,
    },
}

