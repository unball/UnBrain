import json
import os
import numpy as np

def load_replacements_json():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "..", "world", "replacements.json")
    with open(json_path, "r") as f:
        return json.load(f)

def calculate_teleport_positions(foul_name, is_kicker, is_left_side, n_robots_total, quadrant, is_goalie_top=True):
    data = load_replacements_json()
    if foul_name not in data:
        return []

    mode = "5v5" if n_robots_total >= 5 else "3v3"
    foul_data = data[foul_name][mode]
    
    role_key = "foul_kicker" if is_kicker else "foul_receiver"
    
    # Mapeamento genérico dos papéis:
    # Em UnBrain, usualmente 0=Atacante, 1=Goleiro, 2=Zagueiro/Supporter
    # Vamos usar essa mesma ordem padrão caso os ids não estejam amarrados,
    # mas o ideal é o usuário poder ver isso na UI.
    roles_order = ["attacker", "goalkeeper", "supporter", "defender", "midfielder"]
    
    placements = {}
    for i in range(n_robots_total):
        if i < len(roles_order):
            role_name = roles_order[i]
            if role_name in foul_data:
                place = foul_data[role_name][role_key]
                x = place["x"]
                y = place["y"]
                ori = place["ori"]
                
                # Regras de inversão do VSSReferee
                if is_left_side:
                    x = -x
                    # ori precisa ser espelhado (180 - ori) se for esquerda?
                    # No VSSReferee, reflect() inverte o X e inverte o ângulo:
                    # ori = Angle::pi - ori
                    ori = np.pi - np.deg2rad(ori)
                else:
                    ori = np.deg2rad(ori)
                    
                # Free ball quadrants
                if foul_name == "FREE_BALL":
                    # Se quadrante for 3 ou 4 (inferiores), inverte o Y (conforme replacer.cpp linha 344)
                    if quadrant in [3, 4]:
                        y = -y

                # Goal Kick rand
                if foul_name == "GOAL_KICK" and role_name == "goalkeeper" and is_kicker:
                    if not is_goalie_top:
                        y = -y

                placements[i] = {"x": x, "y": y, "th": ori}

    return placements

def apply_safe_jitter(placements, field_maxX, field_maxY, seed=None):
    """
    Aplica ruído (jitter) às posições e orientações dos robôs para simular imprecisões
    do ambiente real e evitar sobreposição perfeita.
    
    Equações de Jitter:
    O ruído translacional segue uma Distribuição Gaussiana Bivariada:
      x' = x + N(mu=0, sigma=0.05)
      y' = y + N(mu=0, sigma=0.05)
    O ruído rotacional segue uma Gaussiana simples:
      th' = th + N(mu=0, sigma=15 graus em radianos)
      
    Clamp (Restrição de Borda):
    Para evitar que o robô atravesse os limites físicos do campo (e colida com as paredes),
    limitamos as coordenadas finais ao intervalo [-maxX + raio, maxX - raio].

    seed=None usa entropia do OS (comportamento padrão — cada restart é estocástico).
    Passe um int apenas para reprodutibilidade explícita em testes.
    """
    rng = np.random.default_rng(seed)
    
    sigma_xy = 0.05 # Desvio padrão aproximado de 5 cm (0.05 m)
    sigma_theta = np.deg2rad(15.0) # Desvio padrão de 15 graus
    
    # Raio aproximado do robô para evitar inserção dentro das paredes (ex: 3.75 cm)
    robot_radius = 0.0375
    
    safe_maxX = field_maxX - robot_radius
    safe_maxY = field_maxY - robot_radius
    
    jittered = {}
    for rid, pose in placements.items():
        x = pose["x"]
        y = pose["y"]
        th = pose["th"]
        
        # Amostragem da Bivariada
        dx, dy = rng.normal(0.0, sigma_xy, 2)
        dth = rng.normal(0.0, sigma_theta)
        
        new_x = x + dx
        new_y = y + dy
        new_th = th + dth
        
        # Limitadores baseados no clamp matemático
        new_x = float(np.clip(new_x, -safe_maxX, safe_maxX))
        new_y = float(np.clip(new_y, -safe_maxY, safe_maxY))
        
        # Normalização angular
        new_th = float((new_th + np.pi) % (2 * np.pi) - np.pi)
        
        jittered[rid] = {"x": new_x, "y": new_y, "th": new_th}
        
    return jittered

def calculate_ball_teleport(foul_name, quadrant, is_left_side, field_length, field_width):
    # Baseado nas regras do VSSReferee
    markX = (field_length / 2.0) - 0.20 # fieldFBMarkX aproximado (depende das constantes do campo real, mas 0.2m da borda é comum)
    markY = (field_width / 2.0) - 0.20
    goalKickX = (field_length / 2.0) - 0.15
    penaltyMarkX = (field_length / 2.0) - 0.375 # ou markX se 3v3

    if foul_name == "KICKOFF":
        return 0.0, 0.0
    elif foul_name == "FREE_BALL":
        if quadrant == 1: return markX, markY
        elif quadrant == 2: return -markX, markY
        elif quadrant == 3: return -markX, -markY
        elif quadrant == 4: return markX, -markY
    elif foul_name == "GOAL_KICK":
        y_val = 0.2 # Valor hardcoded aproximado da stretch
        if is_left_side: return -goalKickX, y_val
        else: return goalKickX, y_val
    elif foul_name == "PENALTY_KICK":
        # Quem bate a falta (kicker) está do lado contrário do gol que será atacado.
        # Se is_left_side == True: kicker é o time da esquerda, logo ataca o gol da direita.
        # Portanto, a bola deve ficar na marca de pênalti do lado direito (penaltyMarkX positivo).
        if is_left_side: 
            return penaltyMarkX, 0.0
        else:
            return -penaltyMarkX, 0.0
    elif foul_name == "FREE_KICK":
        pass 
        
    return 0.0, 0.0
