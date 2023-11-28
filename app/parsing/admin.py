from django.contrib import admin
from .models import (
    TotalCoinModel, KucoinModel, GarantexModel, GateioModel, HodlHodlModel, 
    HuobiModel, BybitModel
)


class BaseParsingAdmin(admin.ModelAdmin):
    list_display = ('name', 'fiat', 'token', 'buy_sell', 'price', 'payments', 
                    'order_q', 'order_p', 'lim_min', 'lim_max', 'available')
    list_filter = ('fiat', 'token', 'buy_sell')
    search_fields = ('name',)

admin.site.register(TotalCoinModel, BaseParsingAdmin)
admin.site.register(KucoinModel, BaseParsingAdmin)
admin.site.register(GarantexModel, BaseParsingAdmin)
admin.site.register(GateioModel, BaseParsingAdmin)
admin.site.register(HodlHodlModel, BaseParsingAdmin)
admin.site.register(HuobiModel, BaseParsingAdmin)
admin.site.register(BybitModel, BaseParsingAdmin)