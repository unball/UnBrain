# UnBrain
Sistema principal da UnBall que agrega as áreas de visão, estratégia, comunicação e controle.

```bash
#for it to run
sudo adduser $USER dialout
sudo chmod a+rw /dev/ttyUSB* #*related to the port
sudo apt install python3-gi
python3.8 src/main.py --team-color blue --team-side left --static-entities
python3.8 src/main.py --team-color blue --team-side left --static-entities --debug #for a debug mode
python3.8 src/main.py --team-color blue --team-side left --static-entities --referee #for a referee mode
```
To end the program please to 

```bash
ctrl + z
#and 
kill %1
```
install requirements

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install python3.8 python3.8-dev python3.8-venv
sudo apt-get install python3.8 python3-dev python3-venv

#create a venv
python3.8 -m venv env
source env/bin/activate
#install requirements into it
pip install -r requirements.txt
```

please compile the proto files
```bash
cd src/client/protobuf
./protobuf.sh
```
