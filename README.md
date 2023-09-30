# UnBrain
Sistema principal da UnBall que agrega as áreas de visão, estratégia, comunicação e controle.

```bash
#for it to run
python3 src/main.py --team-color blue --team-side left
```

install requirements

```bash
apt-get install python3.8 python3.8-dev python3.8-venv

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
