#!/bin/bash -e

# pulseaudio
systemctl enable pulseaudio

#pivumeter
cd /root/pivumeter
aclocal && libtoolize
autoconf && automake --add-missing
./configure && make
make install

# mpd
mkdir /home/transistor/music/
chown transistor:transistor /home/transistor/music/
cd /root/python-mpd2
python3 setup.py install

# physical interface
useradd -r -s /bin/false radio-interface
adduser radio-interface gpio
echo 'radio-interface ALL=(ALL) NOPASSWD: /sbin/shutdown' > /etc/sudoers.d/010_radio-interface-shutdown
chmod 0440 /etc/sudoers.d/010_radio-interface-shutdown
systemctl enable radio-interface
# sound in python
pip3 install --upgrade pip setuptools
pip3 install simpleaudio

# web interface
cd /root/ympd
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX:PATH=/usr
make
make install
systemctl enable ympd

# bluetooth
bluetoothctl -- power on
bluetoothctl -- discoverable on
bluetoothctl -- pairable on
systemctl enable bt-agent
