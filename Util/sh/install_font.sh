read -p 'PATH:  ' FONT_PATH

sudo cp ${FONT_PATH} /usr/share/fonts/
sudo fc-cache -f -v
rm ~/.cache/matplotlib -fr
