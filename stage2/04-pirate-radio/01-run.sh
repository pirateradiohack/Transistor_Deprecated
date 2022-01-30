#!/bin/bash -e

# set hostname
install -v -m 644 files/etc/hostname					"${ROOTFS_DIR}/etc/"
install -v -m 644 files/etc/hosts					"${ROOTFS_DIR}/etc/"

# pulseaudio
install -v -m 644 files/etc/systemd/system/pulseaudio.service		"${ROOTFS_DIR}/etc/systemd/system/"
install -v -m 644 files/etc/pulse/client.conf				"${ROOTFS_DIR}/etc/pulse/"
install -v -m 644 files/etc/pulse/default.pa				"${ROOTFS_DIR}/etc/pulse/"

# pulseaudio first boot volume
install -v -m 644 files/transistor_first_boot 				"${ROOTFS_DIR}/transistor_first_boot"

# mpd
install -v -m 644 files/etc/mpd.conf					"${ROOTFS_DIR}/etc/"

# physical interface (aka buttons)
install -v -m 644 files/etc/systemd/system/radio-interface.service	"${ROOTFS_DIR}/etc/systemd/system/"
mkdir "${ROOTFS_DIR}/usr/local/lib/radio-interface/"
install -v -m 644 files/usr/local/lib/radio-interface/interface.py	"${ROOTFS_DIR}/usr/local/lib/radio-interface/"
install -v -m 644 files/usr/local/lib/radio-interface/audio.py		"${ROOTFS_DIR}/usr/local/lib/radio-interface/"
install -v -m 644 files/usr/local/lib/radio-interface/system.py		"${ROOTFS_DIR}/usr/local/lib/radio-interface/"
install -v -m 644 files/usr/local/lib/radio-interface/display.py	"${ROOTFS_DIR}/usr/local/lib/radio-interface/"
install -v -m 644 files/usr/local/lib/radio-interface/helpers.py	"${ROOTFS_DIR}/usr/local/lib/radio-interface/"
install -v -m 644 files/usr/local/lib/radio-interface/sleep-timer.wav 	"${ROOTFS_DIR}/usr/local/lib/radio-interface/"

# shutdown daemon (to cut off power completely on shutdown)
mkdir -p "${ROOTFS_DIR}/lib/systemd/system-shutdown/"
install -v -m 755 files/lib/systemd/system-shutdown/gpio-poweroff	"${ROOTFS_DIR}/lib/systemd/system-shutdown/"

# web interface
install -v -m 644 files/etc/systemd/system/ympd.service			"${ROOTFS_DIR}/etc/systemd/system/"
git clone https://github.com/pirateradiohack/ympd.git			"${ROOTFS_DIR}/root/ympd"

# radio browser service
mkdir "${ROOTFS_DIR}/usr/local/lib/radio-browser/"
install -v -m 644 files/usr/local/lib/radio-browser/radio-browser.py 	"${ROOTFS_DIR}/usr/local/lib/radio-browser/"
install -v -m 644 files/etc/systemd/system/radio-browser.service 	"${ROOTFS_DIR}/etc/systemd/system/"

# radio settings interface
mkdir "${ROOTFS_DIR}/usr/local/lib/radio-settings/"
cp -r files/usr/local/lib/radio-settings/* 				"${ROOTFS_DIR}/usr/local/lib/radio-settings/"
install -v -m 644 files/etc/systemd/system/radio-settings.service 	"${ROOTFS_DIR}/etc/systemd/system/"
install -v -m 644 files/etc/systemd/system/podcasts-updater.service 	"${ROOTFS_DIR}/etc/systemd/system/"

# bluetooth
install -v -m 644 files/etc/bluetooth/main.conf				"${ROOTFS_DIR}/etc/bluetooth/"
install -v -m 644 files/etc/systemd/system/bluetooth-agent.service	"${ROOTFS_DIR}/etc/systemd/system/"
mkdir "${ROOTFS_DIR}/usr/local/sbin/bluetooth-agent/"
install -v -m 644 files/usr/local/sbin/bluetooth-agent/bluezutils.py	"${ROOTFS_DIR}/usr/local/sbin/bluetooth-agent/"
install -v -m 755 files/usr/local/sbin/bluetooth-agent/simple-agent	"${ROOTFS_DIR}/usr/local/sbin/bluetooth-agent/"
install -v -m 644 files/etc/systemd/system/bluetooth-discovery.service	"${ROOTFS_DIR}/etc/systemd/system/"
install -v -m 755 files/usr/local/sbin/bt-discovery			"${ROOTFS_DIR}/usr/local/sbin/"

# wifi setup
install -v -m 600 files/etc/hostapd/hostapd.conf 			"${ROOTFS_DIR}/etc/hostapd/"
install -v -m 644 files/etc/systemd/system/accesspoint@.service		"${ROOTFS_DIR}/etc/systemd/system/"
install -v -m 644 files/etc/wpa_supplicant/wpa_supplicant-wlan0.conf 	"${ROOTFS_DIR}/etc/wpa_supplicant/"
mkdir "${ROOTFS_DIR}/etc/systemd/system/wpa_supplicant@wlan0.service.d/"
install -v -m 644 files/etc/systemd/system/wpa_supplicant@wlan0.service.d/override.conf "${ROOTFS_DIR}/etc/systemd/system/wpa_supplicant@wlan0.service.d/"
install -v -m 644 files/etc/systemd/network/08-wifi.network 		"${ROOTFS_DIR}/etc/systemd/network/"
install -v -m 644 files/etc/systemd/network/12-ap.network 		"${ROOTFS_DIR}/etc/systemd/network/"
