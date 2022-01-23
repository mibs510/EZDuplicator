#!/bin/bash

if [ "$(lsb_release -r | awk '{print $2}')" != "20.04" ]; then
  echo "WARNING: Use Ubuntu 20.04!"
fi

sudo apt update
sudo apt -y upgrade
sudo apt -y install avrdude
# sudo usermod -a -G ${USER} dialout
# sudo usermod -a -G root dialout
sudo apt install btrfs-progs exfat-utils f2fs-tools hfsutils hfsplus hfsprogs jfsutils cryptsetup dmsetup lvm2 \
util-linux nilfs-tools reiser4progs reiserfsprogs udftools xfsprogs xfsdump partclone disktype grub-imageboot isolinux \
makebootfat pxelinux extlinux syslinux syslinux-common syslinux-efi syslinux-legacy syslinux-utils python3.9 virtualenv \
libcairo2-dev libjpeg-dev libgif-dev libpango1.0-dev libgirepository1.0-dev python3-gi python-gobject-2-dev \
gobject-introspection libpython3.9 libpython3.9-dev python3-pip build-essential debhelper devscripts equivs python3-venv \
python3-dev dh-virtualenv python3-setuptools onboard python3-virtualenv glade

rm -rf venv
virtualenv --python=$(which python3.9) venv && source venv/bin/activate && pip install -r requirements.txt && \
echo "" && \
echo "Done!" && \
echo ""