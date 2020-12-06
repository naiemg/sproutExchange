from django import template
from apps.userauth.models import UserProfile

register = template.Library()

@register.simple_tag
def get_user_type(format_string):
    current_user = UserProfile.objects.get(user=request.user)
    return current_user
