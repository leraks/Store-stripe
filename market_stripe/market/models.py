from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    order = models.OneToOneField('Order', blank=True, null=True, on_delete=models.SET_NULL)

class Order(models.Model):
    items = models.ManyToManyField('Item')

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField(default=1000)

    def __str__(self):
        return self.name


    def get_normal_price(self):
        return "{0:.2f}".format(self.price / 100)


    class Meta:
        ordering = ['name']
