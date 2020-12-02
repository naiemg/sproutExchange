from django.urls import path
from apps.portfolio import views

urlpatterns = [
	path('portfolio/', views.read_portfolio),
]