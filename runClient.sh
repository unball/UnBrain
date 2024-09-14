rm -rf env
python3.8 -m venv env
source env/bin/activate     
pip3 install -r requirements.txt
python3.8 src/main.py --team-color blue