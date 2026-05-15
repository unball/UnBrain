# Projeto: Preditor de Estado (visão assíncrona + histórico de comandos) para rodar antes da IA

Este projeto adiciona uma **camada de estimativa/predição de estado** no PC para compensar:
- atraso da visão (captura + processamento),
- jitter de frames,
- execução assíncrona (controle roda mais rápido que a visão),
sem depender de IMU/encoders do robô.

A ideia é:
1) quando chega um frame novo da visão, armazenar `(x,y,θ,t_capture)`
2) manter um histórico de comandos enviados `(v,w,t_send)`
3) estimar o **estado atual** integrando cinemática diferencial (ZOH) e, opcionalmente, aplicando uma **rede neural residual** que corrige o erro do modelo ideal.

---

## Como isso se encaixa no seu código atual

Você já tem:
- `World.VSSVision_update(...)` que atualiza `raw_update(...)` e calcula velocidades.
- controles/estratégias que produzem comandos (IA ou UFC).

O que vamos adicionar:
- `CommandLogger`: registra todos os `(v,w)` enviados com timestamp.
- `StatePredictor`: dado o último frame da visão e o histórico de comandos depois dele, produz `pose_est_now`.
- (opcional) `ResidualNet`: rede pequena que estima `Δx,Δy,Δθ` (ou `Δsin,Δcos`) para corrigir o modelo cinemático.
- `DatasetBuilder`: transforma logs em dataset supervisionado.

---

## Estrutura de pastas

- `state_predictor/`
  - `predictor.py` (integração cinemática + correção residual)
  - `models.py` (MLP residual simples)
  - `logging.py` (logger de comandos e frames)
  - `dataset.py` (constrói dataset a partir do log)
  - `train.py` (treina a rede)
  - `eval.py` (avalia no log)
- `integration_example.patch.md` (passos e trechos para integrar no seu World)

---

## Fluxo online (rodando no jogo)

1) **Thread/callback da visão**
- chama `frame_logger.push_frame(robot_id, x, y, th, t_capture)`

2) **Loop principal (rápido)**
- obtém `pose_est_now = predictor.estimate_now(robot_id, t_now)`
- entrega `pose_est_now` para a IA (no lugar de `robot.pose` cru da visão)
- IA calcula `(v,w)`
- aplica limitadores/saturação
- envia para Wi-Fi
- chama `cmd_logger.push_cmd(robot_id, v, w, t_send)`

---

## Dataset supervisionado (sem IMU)

O label vem da própria visão:
- entrada: frame em `t_k` + histórico de comandos após `t_k`
- label: pose observada no frame seguinte `t_{k+1}` (ou em `t_k + Δ`)

Isso treina um **modelo de transição temporal** e/ou um **residual** sobre a cinemática ideal.

---

## Rodando

### 1) Teste rápido (sem rede)
Use apenas integração cinemática: `ResidualNet` desligada.

### 2) Coleta de log
Salve `frames.jsonl` e `cmds.jsonl` durante partidas.

### 3) Treino residual
`python -m state_predictor.train --frames frames.jsonl --cmds cmds.jsonl --out model.pt`

### 4) Ative no online
Carregue `model.pt` em `StatePredictor(..., model_path="model.pt")`.

---

## Observações importantes

- Use `time.monotonic()` no PC para timestamps.
- Se você não tem `t_capture` real, use `t_receive`, mas a performance cai.
- Sempre trate ângulo com `sin/cos` para evitar wrap.
- A integração usa **ZOH**: o comando vale até o próximo comando.
