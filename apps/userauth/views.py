# django imports
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings

# apps imports
from apps.userauth.forms import UserForm, UserProfileForm, AddressForm
from apps.userauth.models import UserProfile
from apps.gardens.models import Garden
from apps.portfolio.models import Holding
from apps.exchange.models import Order

# third-part apps imports
from address.models import Address

def user_register(request):
	# If already logged in, take user to dashboard
	if request.user.is_authenticated:
		return HttpResponseRedirect('/dashboard')
	else:
		pass

	# registered flag indicating that a user has NOT been created
	registered = False

	# success flag indicating that a valid address has NOT been entered
	success = False

	# Ensures that API key for address validation is present
	addresses = Address.objects.all()
	if settings.GOOGLE_API_KEY:
		google_api_key_set = True
	else:
		google_api_key_set = False

	# Three forms are utilized to process user registration
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)	# Handles authentication
		user_profile_form = UserProfileForm(data=request.POST) # Handles profile
		address_form = AddressForm(data=request.POST) # Handles address
		
		# If all three forms are valid, then post the data back to the database
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

			# Upon creating an account, redirect to the login page
			return HttpResponseRedirect('/login')

		else:
			# display error message upon recieving bad input
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
	# If already logged in, take user to dashboard
	if request.user.is_authenticated:
		return HttpResponseRedirect('/dashboard')
	else:
		pass

	# Prompt user for login credentials
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
			# Redirect to login page if information is incorrect
			# Prmpt users to re enter login information
			return render(request, "userauth/login.html", {'invalid': True })

	else:
		return render(request, 'userauth/login.html', {})

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required
def user_dashboard(request):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	context_dict['current_user'] = current_user

	if current_user.is_farmer == True:
		# Query logged in farmer's gardens
		your_gardens = Garden.objects.filter(owner = current_user)
		context_dict['your_gardens'] = your_gardens
	else:
		# Query logged in patrons's portfolio and past transactions
		your_portfolio = Holding.objects.filter(owner = current_user)
		context_dict['your_portfolio'] = your_portfolio
		past_orders = Order.objects.filter(owner = current_user)
		context_dict['past_orders'] = past_orders
		
		# Get dollar-value of patron's holdings
		total = 0
		for order in past_orders:
			total += order.total_cost
		context_dict['total_asset_value'] = total

	return render(request, 'userauth/dashboard.html', context_dict)
