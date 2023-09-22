ALP-Winners

Lei de controle da velocidade angular:

Valor lido: $\theta_a$ (ângulo atual do robô)

Referência: $\theta_r$ (ângulo calculado pelo UVF)

Erro: $e_{th}$ ($\theta_r$ -$\theta_a$ )

Saída: w (velocidade angular)

$$ w = \dot{\theta_r} + k_w\cdot \sqrt{e_{th}}
$$
------
Main System

$$ v = \min(v_1,v_2,v_3)\\
v_1 = \frac{-K_{\omega} \sqrt{|\theta_e|} + \\sqrt{K_{\omega}^2 |\theta_e| + 4 |\phi| A_m}}{2|\phi|}\\\\


v_2 = \frac{2 \cdot V_m - L \cdot K_{\omega} \sqrt{|\theta_e|} }{2+L \cdot |\phi|}\\\\

v_3 = K_p ||\vec{r}-\vec{P}(1)||\\\\

\phi = \frac{\partial \theta_d}{\partial x} \cos(\theta) + \frac{\partial \theta_d}{\partial y} \sin(\theta)\\\\

\omega = v \cdot \phi + K_{\omega} \cdot \text{sign}(\theta_e) \sqrt{|\theta_e|}
$$