from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from apps.userauth.models import UserProfile, Address

from address.forms import AddressField, AddressWidget

# Form for all users to sign up for an account
class UserForm(forms.ModelForm):
	email = forms.EmailField(required=True)
	password = forms.CharField(widget=forms.PasswordInput())
	confirm_password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password')

	# Make sure passwords match:
	def clean(self):
		cleaned_data = super(UserForm, self).clean()
		password = cleaned_data.get("password")
		confirm_password = cleaned_data.get("confirm_password")

		if password != confirm_password:
			raise forms.ValidationError("Password do not match")

# Form for all users to create a profile
class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		labels = {
			'is_farmer' : 'I would like to create a garden',
		}
		exclude = ['user', 'address']

# Form that handles the validation of addresses from Google API
class AddressForm(forms.ModelForm):
	class Meta:
		model = Address
		exclude = ['user']