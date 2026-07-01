# Relatório de Benchmarking: NeuralStateEstimator vs Kalman Filter

Este relatório explica como interpretar os resultados do novo pipeline de benchmarking visual e matemático introduzido no UnBrain.

## 1. O Gráfico de Benchmarking (`trajectory_comparison.png`)

O script `evaluate.py` gera uma imagem com duas perspetivas diferentes (Subplots 1x2) focadas nas coordenadas espaciais (X e Y) do robô.

### A. Subplot 1: Visão Macro (Esquerda)
Esta vista demonstra o comportamento geral dos filtros ao longo de uma grande trajetória (tipicamente 2000 frames).
- **Visão Ruidosa (Pontos Azuis):** Representa o que o sistema de visão (tracker) reporta ao robô. Apresenta grande dispersão devido ao ruído Gaussiano, encandeamento ou falhas esporádicas.
- **Ground Truth (Linha Preta Tracejada):** É o caminho fisicamente real e exato que o robô percorreu na simulação. O objetivo ideal de qualquer filtro é ficar perfeitamente sobreposto a esta linha.
- **Kalman Filter Legado (Linha Vermelha):** É o traçado produzido pelos 3 filtros independentes uni-dimensionais antigos.
- **Neural Estimator (Linha Verde):** O resultado da inferência da rede neural usando janelas históricas e comandos cinemáticos ($v, \omega$).

### B. Subplot 2: Visão Micro / Zoom-in (Direita)
Esta vista foca-se num subconjunto dinâmico (aprox. 150 frames) onde o robô sofreu altas acelerações ou fez curvas apertadas. 
**Como interpretar a vantagem Neural:**
* **Phase Lag (Atraso de Fase):** Devido à natureza passiva do Kalman e às matrizes reativas limitadas no domínio 1D, notará que a linha **Vermelha** muitas vezes curva um pouco mais tarde do que a linha preta. A curva **Verde** tende a fechar mais a trajetória junto da preta, uma vez que a rede incorpora os comandos ($v, \omega$) atuais (modelo Forward implicitamente apreendido).
* **Robustez a Outliers:** Se o ruído azul divergir abruptamente para um lado num instante específico (dropout de tracking), o Kalman será puxado, originando um "espigão" indesejado. A rede Neural reconhece padrões temporais (devido ao `history_size`) e rejeita estes valores, mantendo a inércia da trajetória intacta.

## 2. A Matemática (RMSE)

Ao correr o script no terminal, notará os números do *Root Mean Squared Error*.

**O que significa um RMSE mais baixo?**
Significa que, na média absoluta global, a distância entre a posição prevista e a real (Ground Truth) é mais reduzida. O script mostra a melhoria em % entre os dois, permitindo-nos quantificar em tempo real qualquer novo ganho por mexer na arquitetura via Optuna (`tune.py`).

## 3. Próximos Passos recomendados
- Depois de correr o `tune.py` e extrair o `best_params.json`, passe os mesmos como argumento ou re-treine os pesos finais com `train.py`.
- Posteriormente, a equipa pode integrar de forma definitiva este objeto Neural, de forma assíncrona, no loop de 60Hz real da interface GTK.
