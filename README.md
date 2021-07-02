# Transistor [![Build Status](https://api.travis-ci.com/pirateradiohack/Transistor.svg?branch=master)](https://travis-ci.com/github/pirateradiohack/Transistor)

Transistor is a receiver for web radios. It takes the form of an image to be burnt onto an SD card. The image comprises an operating system and all the necessary software to stream internet radios on an embedded platform.  

The current hardware kit consists of the following:
- A Raspberry Pi zero
- A DAC / Audio Amplifier (tested with Phat Beat (discontinued) and [Audio Amp Shim](https://shop.pimoroni.com/products/audio-amp-shim-3w-mono-amp))
- An On / Off switch ([OnOff Shim](https://shop.pimoroni.com/products/onoff-shim))
- A power supply / battery charger ([Adafruit PowerBoost 1000C](https://shop.pimoroni.com/products/onoff-shim))
- A LiPo battery
- A Raspio Analog Zero (optional, if you want to plug a potentiometer for the volume setting)
- Physical buttons for the Raspberry Pi GPIO

Features:
- Takes a playlist of web radios
- Manually add / remove radio streams from the web interface
- Play your audio files by uploading them to `/home/transistor/music/` via `scp`
- Various interfaces to control the radio: physical buttons, web interface, command line interface and phone / desktop applications
- Automatically restores the radio station that was playing and volume level after turning off / on.
- Sleep timer: hold the on off button until your hear the confirmation sound (1 second) and the radio will turn off 20 minutes later. Hold it again to push 20 minutes. You can still simply press the on off button to immediately turn off the radio.

## How to get the image

### Ready-to-write image
For your convenience you will find the latest image pre-built. Access it from the [releases](https://github.com/pirateradiohack/Transistor/releases) page. Download and unzip the latest image, it's the zip file called "image" with a date. (It is built automatically from the source code by Travis-ci.)

All you need to do is to configure your wifi on the image. You can also optionally configure your radio streams playlist.

The files to edit are:
- wifi: `/etc/wpa_supplicant/wpa_supplicant.conf` (edit this file as root / sudo)
- (optionally) playlist: `/home/pi/.config/vlc/playlist.m3u` (create this file)

You can edit the files *before* or *after* writing the image to the sd card:
- before: you can mount the `.img`.  
With a modern operating system you probably just have to click the .img.  
With Linux you can use `kpartx` (from the `multipath-tools` package) to be able to mount the partition directly: `sudo kpartx -a path/to/2019-05-23-Transistor-lite.img` followed by `sudo mount /dev/mapper/loop0p2 tmp/ -o loop,rw`  
(you will need to create the mount directory first and check what loop device you are using with `sudo kpartx -l path/to/2019-05-23-Transistor-lite.img`). Then you can edit the files mentionned above. And `sudo umount tmp`.  
You are safe to flash the image.
- after: your operating system probably automounts the partitions.

### building from source
- First clone this repository with `git clone https://github.com/pirateradiohack/Transistor.git`.  
- Configure your wifi settings: copy the file called `config.example` to `config` and edit this last one. You will see where to enter your wifi name, password and country. All 3 settings are necessary. Your changes to this file will be kept in future updates.
- Optionally configure your radio stations: If you create a file called `my-playlist.m3u` with your own list of internet radio streams, it will be installed.
If not, then you can always add stations in the web interface.
- Then build the image. (You can see the whole guide on the official RaspberryPi repo: https://github.com/RPi-Distro/pi-gen). I find it easier to use docker (obviously you need to have docker installed on your system) as there is nothing else to install, just run one command from this directory: `./build-docker.sh`. That's it. On my computer it takes between 15 and 30 minutes. And at the end you should see something like: `Done! Your image(s) should be in deploy/`  
If you don't see that, it's probably that the build failed. It happens to me sometimes for no reason and I find that just re-launching the build with `CONTINUE=1 ./build-docker.sh` finishes the build correctly.  
- You should find the newly created image in the `deploy` directory.

## Write the image to a SD card
Now that you have your image file, you need to write it to a SD card in order to put it in the Raspberry Pi. Choose you favorite method below and once you have your SD card ready you can boot your Raspberry Pi, the first boot can take a minute or two, and then your radio is ready to go.

### graphically
For a user friendly experience you can try [etcher](https://www.balena.io/etcher/) to flash the image to the SD card.

### manually
On linux (and it probably works on Mac too) an example to get it on the SD card would be:  
`sudo dd bs=4M if=deploy/2019-05-23-Piradio-lite.img of=/dev/mmcblk0 conv=fsync`
(of course you need to replace `/dev/mmcblk0` with the path to your own SD card. You can find it with the command `lsblk -f`)
Those settings are recommended by the RaspberryPi instructions.

## Controlling your radio

The radio is equipped with the necessary buttons to turn it on / off, control the volume up and down, and select the next and previous radio stations. Besides that, you can control it remotely, on the network.

The radio connects to the wifi network that was set in the config file. It should receive an IP address from the Internet router. You need to find this IP address in order to control the radio. There are several ways you can do that:

- For convinience, the radio sets its own local domain. Some devices are compatible with this (Android supposedly works, but iOS does not. Linux should be fine if avahi is installed). So you can try to reach the radio at the address `radio.local`.
- The command `nmap 192.168.1.0/24` can list the devices on your network (adapt the network address based on your computer's IP address, most probably the `1` could be another number). You will see a device named `radio.local` along with its IP address.
- Or you could also check your Internet router to get the list of connected devices and their corresponding IP addresses.

### via web interface
You can control your radio via web interface: try to open `http://radio.local` (or the IP address) in a web browser.

### via ssh with a terminal interface
If you prefer the command line, you can ssh into your radio and then use `ncmpcpp` to get a nice terminal interface (see some screenshots here: https://rybczak.net/ncmpcpp/screenshots/).

### via an application
You can use any `mpd` client you like (a non exhaustive list of applications for various platforms can be found here: https://www.musicpd.org/clients/). If you are asked for the port number, it's the default one, 6600. And for the IP address, it's the same thing as above.

## How it is built
The image is built with the official RaspberryPi.org tool (https://github.com/RPi-Distro/pi-gen) to build a Raspbian lite system with all the software needed
to have a working internet radio stream client. It uses `mpd`.

## Motivation
I wanted to have a software that was easy to install on an embedded kit to make an Internet radio receiver.

## Developers
The interesting bits happen in the `stage2/04-pirate-radio` directory. Where files can be added and then instructions can be set for the building tool to create the final OS image.

If you want to test the image locally, without the need to burn it to an SD card, you can use QEMU to emulate the hardware on your system and then create a virtual machine.
- Make sure you have QEMU installed for the arm architecture, you can test with `qemu-system-arm --version`.
- Set `USE_QEMU` to `"1"` or `true` in the config file and then build your image as usual.
- Download the [Buster kernel](https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/kernel-qemu-4.19.50-buster) and the [Device Tree File](https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/versatile-pb.dtb) in the `deploy` directory.
- Execute `qemu-system-arm -kernel kernel-qemu-4.19.50-buster -cpu arm1176 -m 256 -M versatilepb -dtb versatile-pb.dtb -no-reboot -serial stdio -net nic -net user,hostfwd=tcp::2222-:22,hostfwd=tcp::2223-:80 -append "root=/dev/sda2 panic=1 rootfstype=ext4 rw" -hda name_of_your_image`

That should boot the image. You can then `ssh` into it on `localhost` on port 2222, and use port 80 on `localhost` port 2223.

## Hardware
This is the detailed usage of the pins (thanks to https://pinout.xyz). This is mostly of interest when you want to connect the buttons.

OOS stands for On Off Shim  
PB stands for Phat Beat  
AAS stands for Audio Amp Shim
AZ stands for Raspio Analog Zero

Since powers and grounds don't take names, here is their pinout:  
- Power 1: PB / OOS / AZ
- Power 2: PB / AAS / OOS
- Ground 6: OOS / AZ
- Ground 9: OOS / AZ
- Ground 14: AZ
- Ground 20: PB / AZ
- Ground 25: PB / AAS / AZ
- Ground 30: PB / AZ
- Ground 34: PB / AZ
- Ground 39: PB / AAS / AZ

![Pinout](https://github.com/pirateradiohack/PiRadio/blob/master/Pinout.png)
![Pinout Legend](https://github.com/pirateradiohack/PiRadio/blob/master/Legend-Pinout.png)

The first channel of the Raspio Analog Zero (channel 0) is expecting to receive a potentiometer to set the sound volume:
plug the ends of the potentiometer to 3.3v and ground, then plug the wiper (usually found in the middle of the three tabs) into the first channel of the Analog Zero.

## Contribution
Issues and pull requests are welcome.
