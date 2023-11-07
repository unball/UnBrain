# UnBrain

Sistema principal da UnBall que agrega as áreas de estratégia, comunicação e controle.

Desenvolvido em Python3, pode ser executado em sistemas Linux.

Precisa ser executado com a visão desenvolvida para a VSSS chamada de vsss-vision e com o juiz virtual
VSSSReferee [colocar links]

## Histórico de competições onde foi utilizado

- LARC 2023

## Para executar

Primeiro, é necessário instalar as bibliotecas necessárias para executar o sistema. Antes, recomendamos
a configuração de um ambiente virtual tal como se segue:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install python3.8 python3.8-dev python3.8-venv
sudo apt-get install python3.8 python3-dev python3-venv

#Cria o ambiente virutal
python3.8 -m venv venv

# Entra no ambiente virtual
source env/bin/activate

#install requirements into it
pip3 install -r requirements.txt
```

Depois de ativar o ambiente virtual, podemos instalar as dependências nele com o `pip3`

```bash
pip3 install -r requirements.txt
```

Dentro do ambiente virtual, precisamos compilar os arquivos proto para comunicar com o
VSSSReferee e vsss-vision:

```bash
cd src/client/protobuf
./protobuf.sh
```

Por fim, podemos executar o sistema como segue:

```bash
python3 src/main.py --team-color blue --team-side left
```

### Sobre os argumentos no terminal

Podemos usar `python3 src/main.py --help` para saber mais sobre os argumentos que podemos
passar pelo terminal, mas os principais são

- cor do time `--team-color`` que pode ser yellow ou blue
- lado aliado do campo `--team-side`` que pode ser right ou left, sendo que left é o padrão

Esses são os dois argumentos obrigatórios quando for executar o sistema.

Caso precise executar sem o referee, basta colar no terminal o seguinte comando

```bash
python3 src/main.py --team-color blue --team-side left --immediate-start
```

### Problemas que podem aparecer quando executar o sistema

#### Falha ao abrir serial

A falha ao abrir serial pode ser bem comum principalmente em sistemas Linux. Para resolver esse problema, primeiro,
confira se o transmissor está conectado ao seu computador por um cabo USB. Depois, você precisa autorizar a escrita e leitura da porta serial antes de executar.
Para isso, basta digitar no terminal

```bash
sudo chmod a+rw /dev/ttyUSB0
```

Caso não ele não encontre a porta /dev/ttyUSB0, basta procurar a porta na qual o transmissor está conectada no seu sistema operacional. Nesse caso, pode usar o comando

```bash
ls /dev/ttyUSB*
```

E ele irá listar as portas `ttyUSB*` que estão sendo usadas. Basta copiar a que aparecer e substituir no comando de autorizar a porta.
