sudo systemctl get-default
sudo systemctl set-default multi-user

sudo systemctl status sleep.target suspend.target hibernate.target hybrid-sleep.target
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
