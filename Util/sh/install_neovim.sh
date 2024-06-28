wget https://github.com/neovim/neovim/releases/download/stable/nvim-linux64.tar.gz
tar -xzf nvim-linux64.tar.gz
sudo cp -r nvim-linux64/* /usr/local/
rm nvim-linux64.tar.gz
rm -rf nvim-linux64

# curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim.appimage
# chmod u+x nvim.appimage
# sudo mv ./nvim.appimage /usr/bin/nvim

# sudo add-apt-repository ppa:neovim-ppa/unstable
# sudo apt update
# sudo apt install neovim
