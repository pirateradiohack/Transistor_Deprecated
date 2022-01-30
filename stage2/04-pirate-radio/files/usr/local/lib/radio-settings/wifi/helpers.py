from subprocess import run

def set_wifi(SSID, password):
    """Write wpa_supplicant config file to disk."""
    lines = [
        'country=FR',
        'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
        'update_config=1',
        '',
        'network={',
        f'    ssid="{SSID}"',
        f'    psk="{password}"',
        '    key_mgmt=WPA-PSK',
        '}',
    ]
    with open('/etc/wpa_supplicant/wpa_supplicant-wlan0.conf', 'w') as f:
        f.write('\n'.join(lines))

    command = """reboot"""
    run(command.split())
