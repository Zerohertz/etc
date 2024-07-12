sudo fdisk /dev/sda
# p
# d
# ---
# n
# p
# 1
# ENTER * 2
# w
sudo mkfs.ext4 /dev/sda1
