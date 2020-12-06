from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from apps.gardens.models import Garden, Tier, Update, Comment, Album
from apps.gardens.forms import GardenForm, TierForm, UpdateForm, CommentForm
from apps.userauth.models import UserProfile

from datetime import datetime, timezone

@login_required
def create_garden(request):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	
	if current_user.is_farmer == False:
		# If current user is not a farmer, then don't show them this page
		# Instead, redirect them somewhere else
		return HttpResponseRedirect('/dashboard')
	else:
		pass

	if request.method == 'POST':
		garden_form = GardenForm(data=request.POST)
		garden_form.fields['owner'].widget = forms.HiddenInput()
		
		if garden_form.is_valid():
			garden = garden_form.save()
			garden.owner = current_user
			
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
			return HttpResponseRedirect('/garden/'+str(garden.id))
	else:
		garden_form = GardenForm()
		garden_form.fields['owner'].widget = forms.HiddenInput()

	context_dict['garden_form'] = garden_form

	return render(request, 'gardens/create-garden.html', context_dict)

def read_garden(request, garden_id):
	context_dict = {}

	garden = Garden.objects.get(id = garden_id)
	updates = Update.objects.filter(garden=garden)
	
	context_dict['garden'] = garden
	context_dict['updates'] = updates

	tiers = Tier.objects.filter(garden=garden)
	context_dict['tiers'] = tiers

	images = Album.objects.filter(garden=garden)
	context_dict['images'] = images

	return render(request, 'gardens/read-garden.html', context_dict)

@login_required
def update_garden(request, garden_id):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	
	garden = Garden.objects.get(id = garden_id)
	context_dict['garden'] = garden

	if(garden.owner.id != current_user.id):
		# see if the current user owns the garden they are attempting to edit
		return HttpResponseRedirect('/')
	else:
		pass
	
	if request.method == 'POST':
		garden_form = GardenForm(data=request.POST, instance = garden)
		garden_form.fields['owner'].widget = forms.HiddenInput()

		if garden_form.is_valid():
			garden = garden_form.save()
			garden.owner = current_user
			garden.save()

			return HttpResponseRedirect('/garden/'+str(garden.id))
	else:
		garden_form = GardenForm(instance = garden)
		garden_form.fields['owner'].widget = forms.HiddenInput()

	context_dict['garden_form'] = garden_form

	return render(request, 'gardens/update-garden.html', context_dict)

@login_required
def delete_garden(request, garden_id):
	current_user = UserProfile.objects.get(user=request.user)
	
	garden = Garden.objects.get(id = garden_id)

	if(garden.owner.id != current_user.id):
		# see if the current user owns the garden they are attempting to edit
		return HttpResponseRedirect('/')
	else:
		pass

	garden.delete()

	return HttpResponseRedirect('/dashboard')

@login_required
def create_tier(request, garden_id):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	
	garden = Garden.objects.get(id = garden_id)
	context_dict['garden'] = garden

	if(garden.owner.id != current_user.id):
		# see if the current user owns the garden they are attempting to edit
		return HttpResponseRedirect('/')
	else:
		pass

	if request.method == 'POST':
		tier_form = TierForm(data=request.POST)
		tier_form.fields['garden'].widget = forms.HiddenInput()

		if tier_form.is_valid():
			tier = tier_form.save()
			tier.garden = garden

			now = datetime.now(timezone.utc)
			if (tier.estimated_harvest - now).days < 30:
				invalid = True
				context_dict['invalid'] = invalid
				tier_form = TierForm(data=request.POST)
				tier_form.fields['garden'].widget = forms.HiddenInput()
				context_dict['tier_form'] = tier_form
				return render(request, 'gardens/create-tier.html', context_dict)
			else:
				pass

			tier.save()

			return HttpResponseRedirect('/garden/'+str(tier.garden.id))
	else:
		tier_form = TierForm()
		tier_form.fields['garden'].widget = forms.HiddenInput()

	context_dict['tier_form'] = tier_form

	return render(request, 'gardens/create-tier.html', context_dict)

def read_tier(request, garden_id, tier_id):
	pass

@login_required
def update_tier(request, garden_id, tier_id):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	
	garden = Garden.objects.get(id = garden_id)
	context_dict['garden'] = garden

	tier = Tier.objects.get(id=tier_id)
	context_dict['tier'] = tier

	if(garden.owner.id != current_user.id):
		# see if the current user owns the garden they are attempting to edit
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

			return HttpResponseRedirect('/garden/'+str(tier.garden.id))
	else:
		tier_form = TierForm(instance = tier)
		tier_form.fields['garden'].widget = forms.HiddenInput()

	context_dict['tier_form'] = tier_form

	return render(request, 'gardens/update-tier.html', context_dict)

@login_required
def delete_tier(request, garden_id, tier_id):
	current_user = UserProfile.objects.get(user=request.user)
	
	garden = Garden.objects.get(id = garden_id)
	tier = Tier.objects.get(id = tier_id)

	if(garden.owner.id != current_user.id):
		# see if the current user owns the garden they are attempting to edit
		return HttpResponseRedirect('/')
	else:
		pass

	tier.delete()

	return HttpResponseRedirect(f'/garden/{garden.id}')

@login_required
def create_update(request, garden_id):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	
	garden = Garden.objects.get(id = garden_id)
	context_dict['garden'] = garden

	if(garden.owner.id != current_user.id):
		# see if the current user owns the garden they are attempting to edit
		return HttpResponseRedirect('/')
	else:
		pass

	if request.method == 'POST':
		update_form = UpdateForm(data=request.POST)
		update_form.fields['garden'].widget = forms.HiddenInput()

		if update_form.is_valid():
			update = update_form.save()
			update.garden = garden
			update.owner = current_user
			update.save()

			return HttpResponseRedirect('/garden/'+str(garden.id))
	else:
		update_form = UpdateForm()
		update_form.fields['garden'].widget = forms.HiddenInput()

	context_dict['update_form'] = update_form

	return render(request, 'gardens/create-update.html', context_dict)

def read_update(request, garden_id, update_id, update_slug):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)

	update = Update.objects.get(id=update_id)
	comments = Comment.objects.filter(update=update)
	context_dict['update'] = update
	context_dict['comments'] = comments

	if request.method == 'POST':
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

	return render(request, 'gardens/read-update.html', context_dict)

@login_required
def create_comment(request, garden_id, update_id, update_slug):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	
	update = Update.objects.get(id=update_id)
	context_dict['update'] = update

	if request.method == 'POST':
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
