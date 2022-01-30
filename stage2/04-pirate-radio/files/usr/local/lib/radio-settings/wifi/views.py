from django.shortcuts import render
from .forms import WifiSettingsForm
from .helpers import set_wifi


def wifi_settings(request):
    if request.method == 'POST':
        form = WifiSettingsForm(request.POST)
        if form.is_valid():
            SSID = form.cleaned_data.get('name')
            password = form.cleaned_data.get('password')
            set_wifi(SSID, password)
    else:
        form = WifiSettingsForm()
    return render(request, "wifi/wifi_settings.html", {'form': form})
