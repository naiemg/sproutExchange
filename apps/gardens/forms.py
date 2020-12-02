from django import forms 
from apps.gardens.models import Garden, Tier, Update, Comment

class DateInput(forms.DateInput):
    input_type = 'date'

class GardenForm(forms.ModelForm):
    class Meta:
        model = Garden
        exclude = ['amount_raised', 'total_backers', 'date_created', 'active']

class TierForm(forms.ModelForm):
    class Meta:
        model = Tier
        widgets = {'estimated_harvest': DateInput()}
        exclude = ['total_shares_remaining', 'num_backers']

class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        exclude = ['date_published']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        widgets = {
          'text': forms.Textarea(attrs={'rows':2, 'cols':15}),
        }
        exclude = ['date_published']