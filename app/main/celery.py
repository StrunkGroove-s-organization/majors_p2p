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
        'schedule': 30,
    },
    'huobi-task': {
        'task': 'parsing.tasks.huobi',
        'schedule': 15,
    },
    'gateio-task': {
        'task': 'parsing.tasks.gateio',
        'schedule': 15,
    },
    # 'garantex-task': {
    #     'task': 'parsing.tasks.garantex',
    #     'schedule': 5,
    # },
    'totalcoin-task': {
        'task': 'parsing.tasks.totalcoin',
        'schedule': 10,
    },
    'kucoin-task': {
        'task': 'parsing.tasks.kucoin',
        'schedule': 20,
    },
    'hodlhodl-task': {
        'task': 'parsing.tasks.hodlhodl',
        'schedule': 20,
    },

    ### Calculations ###
    'count-two-actions-task': {
        'task': 'count.tasks.count_in_two_actions',
        'schedule': 10,
    },
    'count-three-actions-task': {
        'task': 'count.tasks.count_in_three_actions',
        'schedule': 10,
    },
    
    ### Best Price ###
    'best-price-task': {
        'task': 'count.tasks.create_best_price',
        'schedule': 5,
    },
}

