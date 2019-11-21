from django.contrib import admin

from .models import Products, ShoppingList

admin.site.register(Products)
admin.site.register(ShoppingList)