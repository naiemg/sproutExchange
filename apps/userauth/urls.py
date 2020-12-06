from django.urls import path
from apps.userauth import views

urlpatterns = [
	path('register/', views.user_register),
	path('login/', views.user_login),
	path('logout/', views.user_logout),
	path('dashboard/', views.user_dashboard), 
	#path('account/', views.account_settings),
	#path('change-password/', views.change_password),
]