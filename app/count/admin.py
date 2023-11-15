from django.contrib import admin
from .models import BestLinksInTwoActions, BestLinksInThreeActions


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


class BestLinksAdmin(admin.ModelAdmin):
    list_display = ('spread', 'buy_info', 'sell_info')
    list_filter = (
        ('buy_ad__exchange', custom_titled_filter('Buy Filter')),
        'buy_ad__best_payment', 'buy_ad__fiat','buy_ad__token',
        ('sell_ad__exchange', custom_titled_filter('Sell Filter')),
        'sell_ad__best_payment', 'sell_ad__fiat', 'sell_ad__token'
    )

    def get_info(self, ad):
        return f"{ad.name} ({ad.buy_sell}, {ad.price}, {ad.fiat}, {ad.token}, {ad.best_payment})"

    def buy_info(self, obj):
        ad = obj.buy_ad
        return self.get_info(ad)

    buy_info.short_description = 'Buy Ad Info'

    def sell_info(self, obj):
        ad = obj.sell_ad
        return self.get_info(ad)

    sell_info.short_description = 'Sell Ad Info'

admin.site.register(BestLinksInTwoActions, BestLinksAdmin)
admin.site.register(BestLinksInThreeActions, BestLinksAdmin)