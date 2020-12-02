import uuid
from django.db import models

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('userauth.UserProfile', on_delete=models.CASCADE, blank=True, null=True)
    tier = models.ForeignKey('gardens.Tier', on_delete=models.CASCADE, blank=True, null=True)
    shares = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class Listing(models.Model):
    owner = models.ForeignKey('userauth.UserProfile', on_delete=models.CASCADE, blank=True, null=True)
    tier = models.ForeignKey('gardens.Tier', on_delete=models.CASCADE, blank=True, null=True)
    ask_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_shares = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.tier.name