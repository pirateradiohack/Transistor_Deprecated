from django import forms
from .models import Feed


class FeedCreate(forms.ModelForm):

    class Meta:
        model = Feed
        fields = 'url'
