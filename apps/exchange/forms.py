from django import forms
from apps.exchange.models import Order, Listing

# Form for patron placing order on shares of an existing garden
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        labels = {
			'shares' : 'How many shares would you like to purchase?',
		}

        exclude = []

# Form for patron creating a listing to sell their existing shares
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = []