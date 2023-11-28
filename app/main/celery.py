import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {

    ### Parsing ###
    'bybit-task': {
        'task': 'parsing.tasks.bybit',
        'schedule': 50,
    },
    'huobi-task': {
        'task': 'parsing.tasks.huobi',
        'schedule': 60,
    },
    'gateio-task': {
        'task': 'parsing.tasks.gateio',
        'schedule': 30,
    },
    'garantex-task': {
        'task': 'parsing.tasks.garantex',
        'schedule': 30,
    },
    'totalcoin-task': {
        'task': 'parsing.tasks.totalcoin',
        'schedule': 30,
    },
    'kucoin-task': {
        'task': 'parsing.tasks.kucoin',
        'schedule': 30,
    },
    'hodlhodl-task': {
        'task': 'parsing.tasks.hodlhodl',
        'schedule': 30,
    },

    ## Calculations ###
    'count-two-actions-task': {
        'task': 'count.tasks.count_in_two_actions',
        'schedule': 30,
    },
    'count-three-actions-task': {
        'task': 'count.tasks.count_in_three_actions',
        'schedule': 30,
    },
}

