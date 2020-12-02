from django.contrib import admin
from apps.exchange.models import Order, Listing

admin.site.register(Order)
admin.site.register(Listing)