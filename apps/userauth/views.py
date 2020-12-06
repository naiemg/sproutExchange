from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings

from apps.userauth.forms import UserForm, UserProfileForm, AddressForm
from apps.userauth.models import UserProfile

from address.models import Address

def user_register(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect('/dashboard')
	else:
		pass

	registered = False
	success = False

	addresses = Address.objects.all()
	if settings.GOOGLE_API_KEY:
		google_api_key_set = True
	else:
		google_api_key_set = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		user_profile_form = UserProfileForm(data=request.POST)
		address_form = AddressForm(data=request.POST)
		
		if user_form.is_valid() and user_profile_form.is_valid() and address_form.is_valid():
			usr = user_form.save()
			usr.set_password(usr.password)
			usr.save()

			profile = user_profile_form.save(commit=False)
			profile.user = usr
			profile.save()

			addr = address_form.save(commit=False)
			addr.user = profile
			addr.save()

			success = True
			registered = True

			return HttpResponseRedirect('/login')

		else:
			print(user_form.errors, user_profile_form.errors)

	else:
		user_form = UserForm()
		user_profile_form = UserProfileForm()
		address_form = AddressForm()

	context_dict = {
		'user_form': user_form,
		'user_profile_form': user_profile_form,
		'address_form': address_form,
		'registered': registered,
		'google_api_key_set': google_api_key_set,
		'success': success,
		'addresses': addresses
	}
	return render(request, 'userauth/register.html', context_dict)

def user_login(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect('/dashboard')
	else:
		pass

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/dashboard')
			else:
				return(HttpResponse("Your Account is disabled"))
		else:
			return render(request, "userauth/login.html", {'invalid': True })

	else:
		return render(request, 'userauth/login.html', {})

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')