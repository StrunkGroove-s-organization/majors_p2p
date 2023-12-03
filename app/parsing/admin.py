from django.contrib import admin
from . import models


class BaseParsingAdmin(admin.ModelAdmin):
    list_display = ('name', 'fiat', 'token', 'buy_sell', 'price', 'payments', 
                    'order_q', 'order_p', 'lim_min', 'lim_max', 'available')
    list_filter = ('fiat', 'token', 'buy_sell')
    search_fields = ('name',)

admin.site.register(models.TotalCoinModel, BaseParsingAdmin)
admin.site.register(models.KucoinModel, BaseParsingAdmin)
admin.site.register(models.GarantexModel, BaseParsingAdmin)
admin.site.register(models.GateioModel, BaseParsingAdmin)
admin.site.register(models.HodlHodlModel, BaseParsingAdmin)
admin.site.register(models.HuobiModel, BaseParsingAdmin)
admin.site.register(models.BybitModel, BaseParsingAdmin)


# class BaseInfoAdmin(admin.ModelAdmin):
#     list_display = ('name',)
# admin.site.register(models.BanksParsing, BaseInfoAdmin)
# admin.site.register(models.CryptoParsing, BaseInfoAdmin)

# class BankParsingTotalCoinAdmin(admin.ModelAdmin):
#     list_display = ('name', 'name_platform')
# admin.site.register(models.BanksParsingTotalCoin, BankParsingTotalCoinAdmin)
