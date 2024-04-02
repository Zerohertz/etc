read SSH_PATH

rsync -avhzP -e "ssh" ${SSH_HOST}:${SSH_PATH} /Users/thomas/Downloads/
