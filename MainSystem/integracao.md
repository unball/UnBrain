# Alterações feitas em 01/10/2022 para integração MainSystem-ALP

## Envio de dados para um cliente pickle.

- Modificação na classe Vision:
    - Após o update do mundo, manda um objeto para o cliente pickle no formato:
    
        `
            'Ball':{
                'x': self._world.ball.pos()[0],
                'y': self._world.ball.pos()[1],
                'vx': self._world.ball.vel()[0],
                'vy': self._world.ball.vel()[1]
            },
            'Robots': {
                i: {
                'x': self._world.robot[i].pose()[0],
                'y': self._world.robot[i].pose()[1],
                'orientation': self._world.robot[i].pose()[2],
                'vx': self._world.robot[i].vel()[0],
                'vy': self._world.robot[i].vel()[1],
                'vangular': self._world.robot[i].w()
                }
                for i in range(self._world.n_robots)
            }
        `
- Passo a passo para teste:

    1. Rodar primeiramente o MainSystem:
        `
            ./main.py
        `

        Este possui um servidor pickle instanciado em qualquer instância da classe Vision.
    2. Rodar um clinte pickle:

        `
            python3 client.py
        `
    3. Entrar na aba HLC e executar 