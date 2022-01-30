from django import forms


class WifiSettingsForm(forms.Form):
    name = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)
