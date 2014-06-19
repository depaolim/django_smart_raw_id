from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name


class SingleSale(models.Model):
    product = models.ForeignKey(Product)
    price = models.IntegerField()


class StockSale(models.Model):
    products = models.ManyToManyField(Product)
    price = models.IntegerField()