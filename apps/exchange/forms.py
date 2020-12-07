from django import forms
from apps.exchange.models import Order, Listing

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        labels = {
			'shares' : 'How many shares would you like to purchase?',
		}

        exclude = []

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = []