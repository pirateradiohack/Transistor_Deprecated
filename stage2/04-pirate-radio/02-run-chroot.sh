#!/bin/bash -e

# pulseaudio
systemctl enable pulseaudio

# pulseaudio for python
pip3 install --upgrade pip setuptools
pip3 install pulsectl

#pivumeter
cd /root/pivumeter
aclocal && libtoolize
autoconf && automake --add-missing
./configure && make
make install

# mpd
mkdir -p /home/transistor/audio_library/{music,podcasts}
chown -R transistor:transistor /home/transistor/audio_library/
cd /root/python-mpd2
python3 setup.py install

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

# bluetooth
systemctl enable bluetooth-agent
systemctl enable bluetooth-discovery

# podcasts
pip3 install poca
