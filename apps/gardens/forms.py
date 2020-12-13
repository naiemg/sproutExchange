from django import forms 
from apps.gardens.models import Garden, Tier, Update, Comment, Album
import datetime

# Allows for the datepicker to be displayed on the HTML form 
class DateInput(forms.DateInput):
    input_type = 'date'

# Form for gardeners to create a new garden
class GardenForm(forms.ModelForm):
    class Meta:
        model = Garden
        labels = {
			'name' : 'Give your garden a name',
            'description': 'Tell us a little more about your garden',
            'sponsor_deadline': 'Dealine for sponsors',
		}
        widgets = {'sponsor_deadline': DateInput()}
        exclude = ['amount_raised', 'total_backers', 'date_created', 'active']

# Form for gardeners to create a new tier that belongs to their garden
class TierForm(forms.ModelForm):
    class Meta:
        model = Tier
        widgets = {'estimated_harvest': DateInput()}
        exclude = ['total_shares_remaining', 'num_backers']

# Form for gardeners to send updates to their patrons
class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        exclude = ['date_published']

# Form for anyone (patrons/gardeners) to comment back on updates
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        widgets = {
          'text': forms.Textarea(attrs={'rows':2, 'cols':15}),
        }
        labels = {
			'text' : 'Comment:',
		}

        exclude = ['date_published']

# Form for gardeners to create upload images to their garden profile
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['field_name']
        exclude = ['garden']
