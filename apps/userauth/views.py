from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

from apps.userauth.forms import UserForm, UserProfileForm
from apps.userauth.models import UserProfile

def user_register(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect('/dashboard')
	else:
		pass

	registered = False
	
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		user_profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and user_profile_form.is_valid():
			usr = user_form.save()

			usr.set_password(usr.password)
			usr.save()

			profile = user_profile_form.save(commit=False)
			profile.user = usr
			profile.save()

			registered = True

			return HttpResponseRedirect('/login')

		else:
			print(user_form.errors, user_profile_form.errors)

	else:
		user_form = UserForm()
		user_profile_form = UserProfileForm()

	return render(request, 'userauth/register.html',
			{'user_form': user_form, 'user_profile_form': user_profile_form, 'registered': registered})

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