# sudo fdisk -l /dev/sda
# sudo apt-get install exfat-fuse
sudo mkdir -p /mnt/HDD
sudo mount -t exfat /dev/sda1 /mnt/HDD