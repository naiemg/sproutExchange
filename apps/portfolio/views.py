from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from apps.exchange.models import Order, Listing
from apps.gardens.models import Garden, Tier
from apps.portfolio.models import Holding
from apps.userauth.models import UserProfile

# Function: read_portfolio
# Description: Allows patrons to view all of their investments

@login_required
def read_portfolio(request):
	context_dict = {}
	
	# Get the current user and all of their holdings
	current_user = UserProfile.objects.get(user=request.user)

	holdings = Holding.objects.filter(owner=current_user)
	context_dict['holdings'] = holdings

	# Displays their holdings on the HTML page
	return render(request, 'portfolio/read-portfolio.html', context_dict)
