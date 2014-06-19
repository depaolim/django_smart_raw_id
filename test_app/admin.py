from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import site as admin_site

from smart_raw_id import SmartRawIdMixin

from .models import *


class ProductAdmin(ModelAdmin):
    pass


class SingleSaleAdmin(SmartRawIdMixin, ModelAdmin):
    list_display = ('id', 'product', 'price')
    raw_id_fields = ('product', )


class StockSaleAdmin(SmartRawIdMixin, ModelAdmin):
    list_display = ('id', 'price')
    raw_id_fields = ('products', )


admin_site.register(Product, ProductAdmin)
admin_site.register(SingleSale, SingleSaleAdmin)
admin_site.register(StockSale, StockSaleAdmin)
