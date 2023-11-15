from django.contrib import admin
from .models import TotalCoin, Kucoin


class BaseParsingAdmin(admin.ModelAdmin):
    list_display = ('name', 'fiat', 'token', 'buy_sell', 'price', 'payments', 
                    'order_q', 'order_p', 'lim_min', 'lim_max', 'available')
    list_filter = ('fiat', 'token', 'buy_sell')
    search_fields = ('name',)

admin.site.register(TotalCoin, BaseParsingAdmin)
admin.site.register(Kucoin, BaseParsingAdmin)