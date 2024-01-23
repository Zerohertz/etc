sudo apt-get install libncurses5-dev libncursesw5-dev -y
sudo apt-get install libudev-dev libsystemd-dev -y
sudo apt-get install libdrm-dev -y

rm -rf nvtop
git clone https://github.com/Syllo/nvtop.git
mkdir -p nvtop/build && cd nvtop/build
cmake .. -DNVIDIA_SUPPORT=ON -DAMDGPU_SUPPORT=ON -DINTEL_SUPPORT=ON
make

sudo make install
cd ../..
rm -rf nvtop
