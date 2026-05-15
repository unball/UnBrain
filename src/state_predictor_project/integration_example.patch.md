# Integração no seu código (exemplo)

Abaixo vai um roteiro prático (com trechos) para integrar sem quebrar sua arquitetura.

## 1) Criar instâncias globais (PC-side)

Em algum ponto central (onde você cria o `World` / loop principal):

```python
from state_predictor import CommandLogger, FrameLogger, StatePredictor
import time

cmd_logger = CommandLogger()
frame_logger = FrameLogger()

predictor = StatePredictor(
    cmd_logger=cmd_logger,
    frame_logger=frame_logger,
    tau_act=0.02,           # chute inicial (ajuste por teste)
    use_residual=False,     # comece sem rede
)
```

## 2) Registrar frames assim que a visão atualizar

No seu `World.VSSVision_update(...)` (ou `update_main_vision(...)`), logo após atualizar os robôs:

```python
t_cap = time.monotonic()  # ideal: timestamp do frame (captura). se não tiver, use receive.
frame_logger.push(robot_id, robot.x, robot.y, robot.th, t_cap)
```

Obs: se a sua visão já traz timestamp do frame, use aquele.

## 3) No loop rápido, usar estado estimado antes da IA

Antes de chamar a IA para decidir, faça:

```python
t_now = time.monotonic()
pose_est = predictor.estimate_now(robot_id, t_now)
if pose_est is not None:
    # substitui temporariamente a pose usada pela IA
    # (opção 1) passe pose_est para o método de observação
    # (opção 2) injete em campos específicos do Robot (ex.: robot.xvec.add(pose_est[0]) etc.)
```

Recomendação: não sobrescrever definitivamente a visão; mantenha um `robot.pose_est` separado.

## 4) Registrar comandos enviados

No ponto onde você envia `(v,w)` para o robô (PC->Wi-Fi):

```python
t_send = time.monotonic()
cmd_logger.push(robot_id, v_cmd, w_cmd, t_send)
```

## 5) (Opcional) Ativar rede residual depois

Após coletar logs e treinar:

```bash
python -m state_predictor.train --frames frames.jsonl --cmds cmds.jsonl --out model.pt
```

E no online:

```python
predictor = StatePredictor(..., use_residual=True, model_path="model.pt")
```

---

# Projeto de testes (de verdade)

## Fase A — baseline e métricas

1) Grave logs por 5–10 min com IA rodando:
- frames (x,y,θ,t)
- cmds (v,w,t)

2) Defina métricas offline:
- erro 1-step: ||pose_{k+1} - pred(pose_k, cmds)|| 
- erro de heading (angError)

3) Ajuste `tau_act` manualmente para minimizar erro médio.

## Fase B — integração cinemática no online

1) Use `predictor.estimate_now()` e alimente a IA com `pose_est`.
2) Compare:
- oscilação (variação de w)
- tempo para alinhar heading
- overshoot em curva

## Fase C — residual supervisionado

1) Treine residual no seu log.
2) Compare offline (MSE) e online (métricas de controle).
3) Re-treine com logs novos se o piso/bateria mudar.

## Fase D — estresse de rede

1) Injete jitter artificial no PC (sleep aleatório no loop).
2) Injete perda de frame (ignore alguns frames).
3) Verifique se `pose_est` mantém estabilidade.

---

## Checklist de aceitação

- Com o preditor, o robô deve reduzir zig-zag em perseguição.
- A IA deve parar de "corrigir atraso" (menos alternância de w).
- Ganhos/limites podem ser aumentados sem instabilidade (em comparação ao baseline).
