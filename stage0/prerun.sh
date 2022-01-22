#!/bin/bash -e

if [ ! -d "${ROOTFS_DIR}" ] || [ "${USE_QCOW2}" = "1" ]; then
	bootstrap ${RELEASE} "${ROOTFS_DIR}" http://raspbian.raspberrypi.org/raspbian/
#	bootstrap ${RELEASE} "${ROOTFS_DIR}" http://mirror.nl.leaseweb.net/raspbian/raspbian/
fi
