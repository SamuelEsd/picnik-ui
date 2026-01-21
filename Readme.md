To run the web ui:

Recommended version of python: 3.13.0

if having a different version installed you can use pyenv

pyenv install 3.13.0
pyenv local 3.13.0

sudo apt install python3-pip

source streamlit_env/bin/activate
sudo apt install python3-pip
pip install -r requirements.txt

streamlit run main.py



modules required:

streamlit
scipy
seaborn
picknic
plotly