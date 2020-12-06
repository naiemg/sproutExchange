from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from apps.exchange.models import Order, Listing
from apps.gardens.models import Garden, Tier
from apps.userauth.models import UserProfile
from apps.exchange.forms import OrderForm, ListingForm
from apps.portfolio.models import Holding

@login_required
def create_order(request, tier_id):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	tier = Tier.objects.get(id=tier_id)

	# Dont let users buy shares if there are none available
	if tier.total_shares_remaining == 0:
		return HttpResponseRedirect('/')
	else:
		pass
	
	if current_user.is_farmer == True:
		# If current user is a farmer, then don't show them this page
		# Instead, redirect them somewhere else
		return HttpResponseRedirect('/dashboard')
	else:
		pass

	if request.method == 'POST':
		order_form = OrderForm(data=request.POST)
		order_form.fields['owner'].widget = forms.HiddenInput()
		order_form.fields['tier'].widget = forms.HiddenInput()
		order_form.fields['total_cost'].widget = forms.HiddenInput()

		if order_form.is_valid():
			order = order_form.save()
			order.owner = current_user
			order.tier = tier
			order.total_cost = order.shares * tier.price_per_share
			
			if order.shares > tier.total_shares_remaining:
				invalid = True
				
				context_dict['invalid'] = invalid
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
			garden.total_backers += 1
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
				# if this is the first time user is pruchasing these shares
				holding = Holding.objects.create(owner=current_user, tier=tier, total_shares=order.shares)
				holding.save()
			
			return HttpResponseRedirect('/order/'+str(order.id))
	else:
		order_form = OrderForm()
		order_form.fields['owner'].widget = forms.HiddenInput()
		order_form.fields['tier'].widget = forms.HiddenInput()
		order_form.fields['total_cost'].widget = forms.HiddenInput()

	context_dict['order_form'] = order_form

	return render(request, 'exchange/create-order.html', context_dict)

@login_required
def read_order(request, order_id):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)

	order = Order.objects.get(id=order_id)
	context_dict['order'] = order

	if current_user.id != order.owner.id:
		return HttpResponseRedirect('/')
	else:
		pass
	
	return render(request, 'exchange/read-order.html', context_dict)

@login_required
def create_listing(request, tier_id):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	tier = Tier.objects.get(id=tier_id)
	
	try:
		holding = Holding.objects.get(owner=current_user, tier=tier)
	except:
		return HttpResponseRedirect('/')

	if request.method == 'POST':
		listing_form = ListingForm(data=request.POST)
		listing_form.fields['owner'].widget = forms.HiddenInput()
		listing_form.fields['tier'].widget = forms.HiddenInput()

		if listing_form.is_valid():
			listing = listing_form.save()
			listing.owner = current_user
			listing.tier = tier
			listing.active = True
			
			if listing.total_shares > holding.total_shares-holding.total_shares_listed:
				invalid = True
				
				context_dict['invalid'] = invalid
				listing_form = ListingForm()
				listing_form.fields['owner'].widget = forms.HiddenInput()
				listing_form.fields['tier'].widget = forms.HiddenInput()
				listing_form.fields['active'].widget = forms.HiddenInput()

				context_dict['listing_form'] = listing_form

				return render(request, 'exchange/create-listing.html', context_dict)
			else:
				pass			
			
			listing.save()

			# Decrement the total shares from sellers portfolio
			print(listing.total_shares)
			holding.total_shares_listed += listing.total_shares
			holding.save()

			return HttpResponseRedirect('/portfolio')
	else:
		listing_form = ListingForm()
		listing_form.fields['owner'].widget = forms.HiddenInput()
		listing_form.fields['tier'].widget = forms.HiddenInput()
		listing_form.fields['active'].widget = forms.HiddenInput()

	context_dict['listing_form'] = listing_form

	return render(request, 'exchange/create-listing.html', context_dict)

def all_listings(request):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)

	listings = Listing.objects.all()
	context_dict['listings'] = listings

	tiers = Tier.objects.filter(total_shares_remaining__gt = 0)
	context_dict['tiers'] = tiers
	
	return render(request, 'exchange/all-listings.html', context_dict)


@login_required
def delete_listing(request, listing_id):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)
	listing = Listing.objects.get(id=listing_id)
	tier = listing.tier
	
	if current_user.id != listing.owner.id:
		return HttpResponseRedirect('/')
	else:
		pass
	
	holding = Holding.objects.get(owner=current_user, tier=tier)
	holding.total_shares_listed -= listing.total_shares
	holding.save()

	listing.delete()

	return HttpResponseRedirect('/portfolio')

@login_required
def purchase_listing(request, listing_id):
	context_dict = {}
	
	current_user = UserProfile.objects.get(user=request.user)

	listing = Listing.objects.get(id=listing_id)
	tier = listing.tier
	context_dict['listing'] = listing

	seller_holding = Holding.objects.get(owner=listing.owner, tier=tier)

	# end listing
	listing.active = False
	listing.save()

	# remove shares from sellers portfolio
	seller_holding.total_shares -= listing.total_shares
	seller_holding.total_shares_listed -= listing.total_shares
	seller_holding.save()
	
	# add shares to buyer's portfolio
	try:
		buyer_holdings = Holding.objects.get(owner=current_user, tier=tier)
		buyer_holdings.total_shares += listing.total_shares
		buyer_holdings.save()
	except:
		new_holding = Holding.objects.create(tier=tier, owner=current_user, total_shares=listing.total_shares)
		new_holding.save()
	# create an order record for buyer
	order = Order.objects.create(tier=tier, owner=current_user, shares=listing.total_shares, total_cost=listing.ask_price)
	order.save()

	# delete listing
	listing.delete()

	return HttpResponseRedirect('/portfolio')