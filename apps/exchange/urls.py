from django.urls import path
from apps.exchange import views

urlpatterns = [
	# Orders
	path('create-order/<int:tier_id>/', views.create_order),
	path('order/<str:order_id>/', views.read_order),
	
	# Listings
	path('create-listing/<int:tier_id>/', views.create_listing),
	path('delete-listing/<int:listing_id>/', views.delete_listing),	path('delete-listing/<int:listing_id>/', views.delete_listing),

	# Sales
	path('purchase-listing/<int:listing_id>/', views.purchase_listing),
	path('all-listings/', views.all_listings),
]