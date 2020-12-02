from django.db import models

class Holding(models.Model):
    owner = models.ForeignKey('userauth.UserProfile', on_delete=models.CASCADE, blank=True, null=True)
    tier = models.ForeignKey('gardens.Tier', on_delete=models.CASCADE, blank=True, null=True)
    total_shares = models.PositiveIntegerField()
    total_shares_listed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.tier.name