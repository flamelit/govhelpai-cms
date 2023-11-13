# Initial setup on Fedora
dnf install -y vim git unzip

# python version: 3.11.2

useradd streamlit
passwd streamlit #govhelpllm
su - streamlit

# generate SSH key


mkdir -p /home/streamlit/venv/
mkdir -p /home/streamlit/app/
python -m venv /home/streamlit/venv/govhelpai

git clone git@github.com:tom-flamelit/GovHelpAI.git govhelp

exit

# Install and set up AWS CLI
cd /home/streamlit/app
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip

su -
source /home/streamlit/venv/govhelpai/bin/activate
cd ~/govhelp
pip install -r requirements.txt

# Install and set up conda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
conda create -n govhelpai python=3.11
conda activate govhelpai
pip install -r pip-requirements.txt