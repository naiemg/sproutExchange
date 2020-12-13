from django import forms
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from apps.gardens.models import Garden, Tier, Update, Comment, Album
from apps.gardens.forms import GardenForm, TierForm, UpdateForm, CommentForm, ImageUploadForm
from apps.userauth.models import UserProfile, Address

from datetime import datetime, timezone

# Function: create_garden
# Description: Gardener creating a garden upon registration.

@login_required
def create_garden(request):
	context_dict = {}
	
	# Get the current user
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user
	
	if current_user.is_farmer == False:
		# If current user is not a farmer, then don't show them this page
		# Only farmers can create a garden
		return HttpResponseRedirect('/dashboard')
	else:
		pass

	# Form to create a garden
	if request.method == 'POST':
		garden_form = GardenForm(data=request.POST)
		garden_form.fields['owner'].widget = forms.HiddenInput()
		
		if garden_form.is_valid():
			garden = garden_form.save()
			garden.owner = current_user

			# Check to ensure that sponsor_deadline date is at least 1 month away
			# For any dates less than 1 month away, show error message / prompt
			now = datetime.now(timezone.utc)
			if (garden.sponsor_deadline - now).days < 30:
				invalid = True
				context_dict['invalid'] = invalid
				garden_form = GardenForm(data=request.POST)
				garden_form.fields['owner'].widget = forms.HiddenInput()
				context_dict['garden_form'] = garden_form
				return render(request, 'gardens/create-garden.html', context_dict)
			else:
				pass
			
			garden.save()
			# Reditect to that garden's created page
			return HttpResponseRedirect('/garden/'+str(garden.id))
	else:
		garden_form = GardenForm()
		garden_form.fields['owner'].widget = forms.HiddenInput()

	context_dict['garden_form'] = garden_form

	return render(request, 'gardens/create-garden.html', context_dict)

# Function: read_garden
# Description: Allows both patrons and gardeners to view a garden's page
# Parameters: garden_id = the garden that user would like to see

@login_required
def read_garden(request, garden_id):
	context_dict = {}

	# Get current user logged-in
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user

	# Get the garden- all of its updates & available tiers.
	garden = Garden.objects.get(id = garden_id)
	updates = Update.objects.filter(garden=garden)
	
	context_dict['garden'] = garden
	context_dict['updates'] = updates

	tiers = Tier.objects.filter(garden=garden)
	context_dict['tiers'] = tiers

	# User address is only used to get the city & state
	# The rest is hidden for privacy reasons
	address = Address.objects.get(user=current_user)
	context_dict['address'] = address

	# Get all pictures associated with that garden
	images = Album.objects.filter(garden=garden)
	context_dict['images'] = images

	return render(request, 'gardens/read-garden.html', context_dict)

# Function: update_garden
# Description: Only gardeners can update their garden's page
# Parameters: garden_id = the garden that is being updated

@login_required
def update_garden(request, garden_id):
	context_dict = {}
	
	# Get the current user and their garden
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user

	garden = Garden.objects.get(id = garden_id)
	context_dict['garden'] = garden

	# A user can only edit a garden that belongs to them
	# Check to see that they own the garden
	if(garden.owner.id != current_user.id):
		return HttpResponseRedirect('/')
	else:
		pass
	
	if request.method == 'POST':
		# Prepopulate form with existing information previously entered
		garden_form = GardenForm(data=request.POST, instance = garden)
		garden_form.fields['owner'].widget = forms.HiddenInput()

		if garden_form.is_valid():
			garden = garden_form.save()
			garden.owner = current_user
			garden.save()

			# Upon daving, redirect to that garden's page to reflect changes
			return HttpResponseRedirect('/garden/'+str(garden.id))
	else:
		garden_form = GardenForm(instance = garden)
		garden_form.fields['owner'].widget = forms.HiddenInput()

	context_dict['garden_form'] = garden_form

	return render(request, 'gardens/update-garden.html', context_dict)

# Function: delete_garden
# Description: Only gardeners can delete a garden, given that it has no patrons already.
# Parameters: garden_id = the garden that is being deleted

@login_required
def delete_garden(request, garden_id):
	# Get current logged-in user & garden
	current_user = UserProfile.objects.get(user=request.user)
	garden = Garden.objects.get(id = garden_id)

	# A user can only delete a garden that belongs to them
	# Check to see that they own the garden
	if garden.owner.id != current_user.id:
		return HttpResponseRedirect('/')
	else:
		pass

	# Gardens that already have patrons cannot be deleted
	if garden.total_backers > 0:
		messages.error(request,f'This garden has {garden.total_backers} backers & cannot be deleted!')
	else:
		# If the garden has no patrons, then it is okay to delete it
		garden.delete()

	return HttpResponseRedirect('/dashboard')

# Function: create_tier
# Description: Gardeners can create tiers for their gardens that patrons cna purchase.
# Parameters: garden_id = the garden that tiers are being added to

@login_required
def create_tier(request, garden_id):
	context_dict = {}
	
	# Get current logged in user & garden
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user

	garden = Garden.objects.get(id = garden_id)
	context_dict['garden'] = garden

	# A user can only add a tier to a garden that they own
	# Check to see that they own the garden
	if(garden.owner.id != current_user.id):
		return HttpResponseRedirect('/')
	else:
		pass

	if request.method == 'POST':
		tier_form = TierForm(data=request.POST)
		tier_form.fields['garden'].widget = forms.HiddenInput()

		if tier_form.is_valid():
			tier = tier_form.save()
			tier.garden = garden

			# Check to ensure that estimated_harvest date is at least 50 days from garden_sponsor_deadline
			# For any dates less than 50 days away, show error message / prompt
			garden_sponsor_deadline = garden.sponsor_deadline
			if (tier.estimated_harvest - garden_sponsor_deadline).days < 50:
				invalid = True
				context_dict['invalid'] = invalid
				tier_form = TierForm(data=request.POST)
				tier_form.fields['garden'].widget = forms.HiddenInput()
				context_dict['tier_form'] = tier_form
				return render(request, 'gardens/create-tier.html', context_dict)
			else:
				pass

			tier.save()

			# Redirect to that garden's page to reflect the changes
			return HttpResponseRedirect('/garden/'+str(tier.garden.id))
	else:
		tier_form = TierForm()
		tier_form.fields['garden'].widget = forms.HiddenInput()

	context_dict['tier_form'] = tier_form

	return render(request, 'gardens/create-tier.html', context_dict)

# Function: read_tier
# Description: read that tier to the user requesting it

def read_tier(request, garden_id, tier_id):
	# Not really needed
	# But may be useful in the future when creating an API
	pass

# Function: update_tier
# Description: Gardeners can update tiers for their gardens.
# Parameters: 	garden_id = the garden that tiers are belong to
#				tier_id = the tiers being modified

@login_required
def update_tier(request, garden_id, tier_id):
	context_dict = {}
	
	# Get the current user, garden, and tier to be changed
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user

	garden = Garden.objects.get(id = garden_id)
	context_dict['garden'] = garden

	tier = Tier.objects.get(id=tier_id)
	context_dict['tier'] = tier

	# A user can only modify a tier that belongs to a garden that they own
	# Check to see that they own that tier's garden
	if(garden.owner.id != current_user.id):
		return HttpResponseRedirect('/')
	else:
		pass
	
	if request.method == 'POST':
		tier_form = TierForm(data=request.POST, instance = tier)
		tier_form.fields['garden'].widget = forms.HiddenInput()

		if tier_form.is_valid():
			tier = tier_form.save()
			tier.garden = garden
			tier.save()

			# Redirect to that garden's page to reflect the changes
			return HttpResponseRedirect('/garden/'+str(tier.garden.id))
	else:
		tier_form = TierForm(instance = tier)
		tier_form.fields['garden'].widget = forms.HiddenInput()

	context_dict['tier_form'] = tier_form

	return render(request, 'gardens/update-tier.html', context_dict)

# Function: delete_tier
# Description: Gardeners can delete tiers for their gardens, given that no patrons have chose that tier.
# Parameters: 	garden_id = the garden that tiers are belong to
#				tier_id = the tiers being deleted

@login_required
def delete_tier(request, garden_id, tier_id):
	# Get current logged in user, garden, and tier to be deleted
	current_user = UserProfile.objects.get(user=request.user)
	garden = Garden.objects.get(id = garden_id)
	tier = Tier.objects.get(id = tier_id)

	# The user must own the garden that that tier belongs to
	# Otherwise they wont be able to delete something they dont own
	if(garden.owner.id != current_user.id):
		return HttpResponseRedirect('/')
	else:
		pass

	# Tiers that already have patrons cannot be deleted
	# This would involve a complicated refund process, maybe explore in v2.0
	if tier.num_backers > 0:
		messages.error(request,f'This tier has {tier.num_backers} backers & cannot be deleted!')
	else:
		# If there are no backers, you are free to delete it
		tier.delete()

	return HttpResponseRedirect(f'/garden/{garden.id}')

# Function: create_update
# Description: Gardeners can create blogpost updates that are broadcasted to their patrons.
# Parameters: 	garden_id = the garden whose patrons are being updated

@login_required
def create_update(request, garden_id):
	context_dict = {}
	
	# Get the current user and their agrden
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user

	garden = Garden.objects.get(id = garden_id)
	context_dict['garden'] = garden

	# A user can only send updates to patrons of a garden that they own
	# Check to see that the user owns that garden
	if(garden.owner.id != current_user.id):
		return HttpResponseRedirect('/')
	else:
		pass

	# Present form to send update out
	if request.method == 'POST':
		update_form = UpdateForm(data=request.POST)
		update_form.fields['garden'].widget = forms.HiddenInput()

		if update_form.is_valid():
			update = update_form.save()
			update.garden = garden
			update.owner = current_user
			update.save()

			# After creating an update, redirect to the garden page
			return HttpResponseRedirect('/garden/'+str(garden.id))
	else:
		update_form = UpdateForm()
		update_form.fields['garden'].widget = forms.HiddenInput()

	context_dict['update_form'] = update_form

	return render(request, 'gardens/create-update.html', context_dict)

# Function: read_update
# Description: Everyone (gardener & patron) can view an update.
# Parameters: 	garden_id = the garden that the update pertains to
#				update_id = the update that users want to view
#				update_slug = formats the name of the update to-have-this-format in the url

def read_update(request, garden_id, update_id, update_slug):
	context_dict = {}
	
	# Get the current user, the update being requested, and all of
	# the comments associated with that update
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user

	update = Update.objects.get(id=update_id)
	comments = Comment.objects.filter(update=update)
	context_dict['update'] = update
	context_dict['comments'] = comments

	# Present the comment form alongide each post so that users can respond back to it
	if request.method == 'POST':
		comment_form = CommentForm(data=request.POST)
		comment_form.fields['author'].widget = forms.HiddenInput()
		comment_form.fields['update'].widget = forms.HiddenInput()

		if comment_form.is_valid():
			comment = comment_form.save()
			comment.update = update
			comment.author = current_user
			comment.save()

			# After making a comment, redirect users back to the update they just commented on
			return HttpResponseRedirect('/garden/' + str(update.garden.id) + '/update/' + str(update.id) + '/' + str(update.slug))
	else:
		comment_form = CommentForm()
		comment_form.fields['author'].widget = forms.HiddenInput()
		comment_form.fields['update'].widget = forms.HiddenInput()

	context_dict['comment_form'] = comment_form

	return render(request, 'gardens/read-update.html', context_dict)

# Function: create_comment
# Description: Everyone (gardener & patron) can view comment on an update.
# Parameters: 	garden_id = the garden that the update pertains to
#				update_id = the update that users want to comment on
#				update_slug = formats the name of the update to-have-this-format in the url

@login_required
def create_comment(request, garden_id, update_id, update_slug):
	context_dict = {}
	
	# Get the current user, the update being requested
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user

	update = Update.objects.get(id=update_id)
	context_dict['update'] = update

	if request.method == 'POST':
		# comment form is presented to allow them to respond back
		comment_form = CommentForm(data=request.POST)
		comment_form.fields['author'].widget = forms.HiddenInput()
		comment_form.fields['update'].widget = forms.HiddenInput()

		if comment_form.is_valid():
			comment = comment_form.save()
			comment.update = update
			comment.author = current_user
			comment.save()

			return HttpResponseRedirect('/garden/' + str(update.garden.id) + '/update/' + str(update.id) + '/' + str(update.slug))
	else:
		comment_form = CommentForm()
		comment_form.fields['author'].widget = forms.HiddenInput()
		comment_form.fields['update'].widget = forms.HiddenInput()

	context_dict['comment_form'] = comment_form

	return render(request, 'gardens/create-comment.html', context_dict)

# Function: upload_image
# Description: Gardeners can upload images to their garden page
# Parameters: 	garden_id = the garden that the image pertains to

@login_required
def upload_image(request, garden_id):
	context_dict = {}
	
	# Current logged-in user and garden retrieved
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user

	garden = Garden.objects.get(id=garden_id)
	context_dict['garden'] = garden

	if request.method == 'POST':
		# Form presented to upload photo
		# Requesting the file system to be displayed also
		image_upload_form = ImageUploadForm(request.POST, request.FILES)
		if image_upload_form.is_valid():
			image_upload_form.save()
			# Get the current instance object to display in the template
			img = image_upload_form.instance
			img.garden = garden
			img.save()

			# Redirect to the garden's page to see the added image
			return HttpResponseRedirect('/garden/'+str(garden.id))

	else:
		image_upload_form = ImageUploadForm()

	context_dict['image_upload_form'] = image_upload_form

	return render(request, 'gardens/upload-image.html', context_dict)