curl -sfL https://get.k3s.io | sh -s - --docker
sudo cat /etc/rancher/k3s/k3s.yaml
rm -rf ~/.kube
mkdir ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config