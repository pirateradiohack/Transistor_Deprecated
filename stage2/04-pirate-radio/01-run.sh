#!/bin/bash -e

# set hostname
install -v -m 644 files/etc/hostname					"${ROOTFS_DIR}/etc/"
install -v -m 644 files/etc/hosts					"${ROOTFS_DIR}/etc/"

# pulseaudio
install -v -m 644 files/etc/systemd/system/pulseaudio.service		"${ROOTFS_DIR}/etc/systemd/system/"
install -v -m 644 files/etc/pulse/client.conf				"${ROOTFS_DIR}/etc/pulse/"
install -v -m 644 files/etc/pulse/default.pa				"${ROOTFS_DIR}/etc/pulse/"

# pivumeter
git clone https://github.com/pimoroni/pivumeter.git			"${ROOTFS_DIR}/root/pivumeter"
install -v -m 644 "${ROOTFS_DIR}/root/pivumeter/dependencies/etc/asound.conf"		"${ROOTFS_DIR}/etc/"

# mpd
git clone https://github.com/Mic92/python-mpd2.git			"${ROOTFS_DIR}/root/python-mpd2"
install -v -m 644 files/etc/mpd.conf					"${ROOTFS_DIR}/etc/"
if [ -f ../../my-playlist.m3u ]; then
	install -v -m 644 ../../my-playlist.m3u				"${ROOTFS_DIR}/var/lib/mpd/playlists/my-playlist.m3u"
fi

# physical interface (aka buttons)
install -v -m 644 files/etc/systemd/system/radio-interface.service	"${ROOTFS_DIR}/etc/systemd/system/"
mkdir "${ROOTFS_DIR}/usr/local/lib/radio-interface/"
install -v -m 644 files/interface.py					"${ROOTFS_DIR}/usr/local/lib/radio-interface/"
install -v -m 644 files/sleep-timer.wav 				"${ROOTFS_DIR}/usr/local/lib/radio-interface/"

# shutdown daemon (to cut off power completely on shutdown)
mkdir -p "${ROOTFS_DIR}/lib/systemd/system-shutdown/"
install -v -m 755 files/lib/systemd/system-shutdown/gpio-poweroff	"${ROOTFS_DIR}/lib/systemd/system-shutdown/"

# web interface
install -v -m 644 files/etc/systemd/system/ympd.service			"${ROOTFS_DIR}/etc/systemd/system/"
git clone https://github.com/notandy/ympd.git				"${ROOTFS_DIR}/root/ympd"

# bluetooth
install -v -m 644 files/etc/bluetooth/main.conf				"${ROOTFS_DIR}/etc/bluetooth/"
install -v -m 644 files/etc/systemd/system/bluetooth-agent.service	"${ROOTFS_DIR}/etc/systemd/system/"
mkdir "${ROOTFS_DIR}/usr/local/sbin/bluetooth-agent/"
install -v -m 644 files/usr/local/sbin/bluetooth-agent/bluezutils.py	"${ROOTFS_DIR}/usr/local/sbin/bluetooth-agent/"
install -v -m 755 files/usr/local/sbin/bluetooth-agent/simple-agent	"${ROOTFS_DIR}/usr/local/sbin/bluetooth-agent/"
install -v -m 644 files/etc/systemd/system/bluetooth-discovery.service	"${ROOTFS_DIR}/etc/systemd/system/"
install -v -m 755 files/usr/local/sbin/bt-discovery			"${ROOTFS_DIR}/usr/local/sbin/"

# poca
install -v -m 644 files/poca.xml					"${ROOTFS_DIR}/home/transistor/.poca/"
install -v -m 600 files/var/spool/cron/crontabs/transistor		"${ROOTFS_DIR}/var/spool/cron/crontabs/"
chown transistor:crontab /var/spool/cron/crontabs/transistor
