from main.celery import app
from .services import CountActionsInTwo, CountActionsInThree, BestPrices


@app.task
def count_in_two_actions():
    count = CountActionsInTwo()
    return count.count_in_two_actions()


@app.task
def count_in_three_actions():
    count = CountActionsInThree()
    return count.count_in_three_actions()


@app.task
def create_best_price():
    best_price = BestPrices()
    return best_price.create_links()