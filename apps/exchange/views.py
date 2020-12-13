from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from apps.exchange.models import Order, Listing
from apps.gardens.models import Garden, Tier
from apps.userauth.models import UserProfile
from apps.exchange.forms import OrderForm, ListingForm
from apps.portfolio.models import Holding

# Function: create_order
# Description: Responsible for the creation of order records for direct sales between gardens and patrons.
# Parameters: tier_id = tier of a garden being purchased

@login_required
def create_order(request, tier_id):
	context_dict = {}
	
	# Get the current logged-in user
	current_user = UserProfile.objects.get(user=request.user)
	
	# Query for object to be purchased
	tier = Tier.objects.get(id=tier_id)
	
	# Dont let users buy shares if there are none available
	if tier.total_shares_remaining == 0:
		return HttpResponseRedirect('/')
	else:
		pass
	
	# If current user is a farmer, then don't show them this page
	# Gardeners can not purchase shares in a garden
	if current_user.is_farmer == True:
		return HttpResponseRedirect('/dashboard')
	else:
		pass

	# Form to create an order
	if request.method == 'POST':

		# Hide these fields because they are already predetermined
		order_form = OrderForm(data=request.POST)
		order_form.fields['owner'].widget = forms.HiddenInput()
		order_form.fields['tier'].widget = forms.HiddenInput()

		# Total cost to be calculated later, hide from user
		order_form.fields['total_cost'].widget = forms.HiddenInput()

		if order_form.is_valid():
			order = order_form.save()
			order.owner = current_user
			order.tier = tier

			# Total Cost = number of shares purchased x the price per each share
			order.total_cost = order.shares * tier.price_per_share
			
			# Users cannot buy more shares than are available for purchase
			if order.shares > tier.total_shares_remaining:
				# Flag that sets off an error message
				invalid = True
				context_dict['invalid'] = invalid
				
				# Redisplay form for user to re-enter information
				order_form = OrderForm()
				order_form.fields['owner'].widget = forms.HiddenInput()
				order_form.fields['tier'].widget = forms.HiddenInput()
				order_form.fields['total_cost'].widget = forms.HiddenInput()
				context_dict['order_form'] = order_form

				return render(request, 'exchange/create-order.html', context_dict)
			else:
				pass			
			
			order.save()
			garden = order.tier.garden

			# The garden now has one more backer
			garden.total_backers += 1

			# Adjust the amount raised for that garden to display the sale
			garden.amount_raised += order.total_cost
			garden.save()

			# Decrement the total shares remining in a tier
			tier.total_shares_remaining -= order.shares
			tier.num_backers += 1
			tier.save()

			# Add shares to user's portfolio
			try:
				# If user already has shares in their portfolio,
				# add new shares to existing shares
				holding = Holding.objects.get(owner=current_user, tier=tier)
				holding.total_shares += order.shares
				holding.save()
			except:
				# if this is the first time user is pruchasing these shares, create a new holding
				holding = Holding.objects.create(owner=current_user, tier=tier, total_shares=order.shares)
				holding.save()
			
			return HttpResponseRedirect('/dashboard')
	else:
		order_form = OrderForm()
		order_form.fields['owner'].widget = forms.HiddenInput()
		order_form.fields['tier'].widget = forms.HiddenInput()
		order_form.fields['total_cost'].widget = forms.HiddenInput()

	context_dict['order_form'] = order_form

	return render(request, 'exchange/create-order.html', context_dict)

# Function: read_order
# Description: A getter function for orders to be read by both patrons and gardens
# Parameters: order_id = order being requested to be viewed

@login_required
def read_order(request, order_id):
	context_dict = {}
	
	# Get the current logged-in user
	current_user = UserProfile.objects.get(user=request.user)

	# Query for the requested order
	order = Order.objects.get(id=order_id)
	context_dict['order'] = order

	if current_user.id != order.owner.id:
		return HttpResponseRedirect('/')
	else:
		pass
	
	return render(request, 'exchange/read-order.html', context_dict)

# Function: create_listing
# Description: Patron creates a listing for their shares to be sold on the secondaries marketplace.
# Parameters: tier_id = type of tier that patron is attempting to sell

@login_required
def create_listing(request, tier_id):
	context_dict = {}
	
	# Get the current logged-in user
	current_user = UserProfile.objects.get(user=request.user)
	tier = Tier.objects.get(id=tier_id)
	
	try:
		# Check current_user's holdings for those shares
		# User can only sell shares that they own
		holding = Holding.objects.get(owner=current_user, tier=tier)
	except:
		# Users cannot sell shares that they dont own
		# redirect them away otherwise
		return HttpResponseRedirect('/')

	# Form processing for creating a listing
	if request.method == 'POST':
		listing_form = ListingForm(data=request.POST)
		listing_form.fields['owner'].widget = forms.HiddenInput()
		listing_form.fields['tier'].widget = forms.HiddenInput()

		if listing_form.is_valid():
			listing = listing_form.save()
			listing.owner = current_user
			listing.tier = tier
			listing.active = True
			
			# User cannot sell more shares than they own
			if listing.total_shares > holding.total_shares-holding.total_shares_listed:
				# Set flag to display an error emssage
				invalid = True
				context_dict['invalid'] = invalid
				
				# Redisplay form for user to re-enter information
				listing_form = ListingForm()
				listing_form.fields['owner'].widget = forms.HiddenInput()
				listing_form.fields['tier'].widget = forms.HiddenInput()
				listing_form.fields['active'].widget = forms.HiddenInput()

				context_dict['listing_form'] = listing_form

				return render(request, 'exchange/create-listing.html', context_dict)
			else:
				pass			
			
			listing.save()

			# Add those shares count to the listing
			holding.total_shares_listed += listing.total_shares
			holding.save()

			return HttpResponseRedirect('/')
	else:
		listing_form = ListingForm()
		listing_form.fields['owner'].widget = forms.HiddenInput()
		listing_form.fields['tier'].widget = forms.HiddenInput()
		listing_form.fields['active'].widget = forms.HiddenInput()

	context_dict['listing_form'] = listing_form

	return render(request, 'exchange/create-listing.html', context_dict)

# Function: all_listings
# Description: Queries all listings available to display to patrons browsing all investment oppurtunities.

def all_listings(request):
	context_dict = {}
	
	# A general query getting all listings
	listings = Listing.objects.all()
	context_dict['listings'] = listings

	# Patrons can only see gardens that have shares available for sale
	# If no shares are available, don't display that garden
	tiers = Tier.objects.filter(total_shares_remaining__gt = 0).exclude(garden__isnull=True)
	context_dict['tiers'] = tiers
	
	return render(request, 'exchange/all-listings.html', context_dict)

# Function: delete_listing
# Description: Patron deletes a listing before anyone buys it; no transaction occurs.
# Parameters: listing_id = listing that they are tying to remove.

@login_required
def delete_listing(request, listing_id):
	context_dict = {}
	
	# Get current user and listing that they're trying to delete
	current_user = UserProfile.objects.get(user=request.user)
	listing = Listing.objects.get(id=listing_id)
	tier = listing.tier
	
	# Users cannot delete a listing that they don't own
	if current_user.id != listing.owner.id:
		return HttpResponseRedirect('/')
	else:
		pass
	
	# Get that listing from their portfolio and add back to it
	# Since they are not selling those shares anymore
	holding = Holding.objects.get(owner=current_user, tier=tier)
	holding.total_shares_listed += listing.total_shares
	holding.save()

	listing.delete()

	return HttpResponseRedirect('/')

# Function: purchase_listing
# Description: Transaction occurs between two patrons in the sale of a listing
# Parameters: listing_id = listing that they are tying to trade.

@login_required
def purchase_listing(request, listing_id):
	context_dict = {}
	
	# Get the current user (buyer)
	current_user = UserProfile.objects.get(user=request.user)

	listing = Listing.objects.get(id=listing_id)
	tier = listing.tier
	context_dict['listing'] = listing

	# Get the seller's portfolio
	seller_holding = Holding.objects.get(owner=listing.owner, tier=tier)

	# end the listing since there is a buyer available
	listing.active = False
	listing.save()

	# remove shares from sellers portfolio
	seller_holding.total_shares -= listing.total_shares
	seller_holding.total_shares_listed -= listing.total_shares
	seller_holding.save()
	
	# add shares to buyer's portfolio
	try:
		# If the buyer has a holding, add it to the existing one
		buyer_holdings = Holding.objects.get(owner=current_user, tier=tier)
		buyer_holdings.total_shares += listing.total_shares
		buyer_holdings.save()
	except:
		# otherwise create a new holding for those shares
		new_holding = Holding.objects.create(tier=tier, owner=current_user, total_shares=listing.total_shares)
		new_holding.save()
	# create an order record for buyer
	order = Order.objects.create(tier=tier, owner=current_user, shares=listing.total_shares, total_cost=listing.ask_price)
	order.save()

	# delete listing
	listing.delete()

	return HttpResponseRedirect('/')