#!/bin/bash -e

if [ ! -d "${ROOTFS_DIR}" ] || [ "${USE_QCOW2}" = "1" ]; then
	bootstrap ${RELEASE} "${ROOTFS_DIR}" http://raspbian.raspberrypi.org/raspbian/
#	bootstrap ${RELEASE} "${ROOTFS_DIR}" http://mirrors.ircam.fr/pub/raspbian/raspbian/
fi
