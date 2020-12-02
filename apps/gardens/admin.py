from django.contrib import admin
from apps.gardens.models import Garden, Tier, Update, Comment

admin.site.register(Garden)
admin.site.register(Tier)
admin.site.register(Update)
admin.site.register(Comment)
