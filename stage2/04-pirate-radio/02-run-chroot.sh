#!/bin/bash -e

# pulseaudio
systemctl enable pulseaudio

# pulseaudio for python
pip3 install --upgrade pip setuptools
pip3 install pulsectl

# mpd
mkdir -p /home/transistor/podcasts
chown -R transistor:transistor /home/transistor/podcasts
pip3 install python-mpd2

# physical interface
useradd -r -s /bin/false radio-interface
adduser radio-interface gpio
echo 'radio-interface ALL=(ALL) NOPASSWD: /sbin/shutdown' > /etc/sudoers.d/010_radio-interface-shutdown
chmod 0440 /etc/sudoers.d/010_radio-interface-shutdown
systemctl enable radio-interface

# sound in python
pip3 install simpleaudio

# web interface
cd /root/ympd
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX:PATH=/usr
make
make install
systemctl enable ympd

# pirate audio screen
pip3 install st7789

# Radio browser
pip3 install pyradios
systemctl enable radio-browser

# Podcasts
pip3 install -r /usr/local/lib/radio-settings/requirements.txt
systemctl enable podcasts-updater

# Radio settings interface
cd /usr/local/lib/radio-settings
python3 manage.py makemigrations && python3 manage.py migrate
systemctl enable radio-settings

# bluetooth
systemctl enable bluetooth-agent
systemctl enable bluetooth-discovery

# wifi
systemctl disable dhcpcd rsyslog avahi-daemon
apt --autoremove -y purge ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog avahi-daemon
rm -r /etc/network /etc/dhcp
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
apt-mark hold avahi-daemon dhcpcd dhcpcd5 ifupdown isc-dhcp-client isc-dhcp-common libnss-mdns openresolv raspberrypi-net-mods rsyslog
systemctl enable systemd-networkd.service systemd-resolved.service
systemctl enable accesspoint@wlan0.service
rfkill unblock wlan
systemctl disable wpa_supplicant.service
rm -rf /etc/wpa_supplicant/wpa_supplicant.conf
systemctl enable wpa_supplicant@wlan0.service
