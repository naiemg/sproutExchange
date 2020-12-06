from django.urls import path
from apps.gardens import views

urlpatterns = [
	path('create-garden/', views.create_garden),
	path('garden/<int:garden_id>/', views.read_garden),
	path('garden/<int:garden_id>/update', views.update_garden),
	path('garden/<int:garden_id>/delete', views.delete_garden),
	
	path('garden/<int:garden_id>/create-tier', views.create_tier),
	path('garden/<int:garden_id>/tier/read-tier', views.read_tier),
	path('garden/<int:garden_id>/tier/<int:tier_id>/update', views.update_tier),
	path('garden/<int:garden_id>/tier/<int:tier_id>/delete', views.delete_tier),

	path('garden/<int:garden_id>/create-update', views.create_update),
	path('garden/<int:garden_id>/update/<int:update_id>/<slug:update_slug>', views.read_update),

	path('garden/<int:garden_id>/update/<int:update_id>/<slug:update_slug>/comment', views.create_comment),

	path('garden/<int:garden_id>/upload-image', views.upload_image),
]