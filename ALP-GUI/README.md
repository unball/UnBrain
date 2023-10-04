# ALP-GUI

Interface gráfica que recebe objetos para serem desenhados no campo via socket UDP. Este repositório contém um cliente que pode ser usado pela sua aplicação para mostrar os objetos.

## Cliente

O cliente se encontra em `src/app/classes/client.py` e pode ser usado de forma singleton, por exemplo para mostrar um robô:

```python3
from app.classes.client import clientProvider

clientProvider().drawRobot(robot.id, robot.x, robot.y, robot.thvec_raw.vec[0], robot.direction)
```

Os objetos são identificados por id, e caso chame-se `drawRobot` mais de uma vez com o mesmo id, ele reposicionará o robô.
