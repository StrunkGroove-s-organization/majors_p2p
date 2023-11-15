from main.celery import app
from .services import CountActionsInTwo, CountActionsInThree


@app.task
def count_in_two_actions():
    count = CountActionsInTwo()
    return count.count_in_two_actions()


@app.task
def count_in_three_actions():
    count = CountActionsInThree()
    return count.count_in_three_actions()