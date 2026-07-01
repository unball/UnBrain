import random
import math

class VisionNoiseSimulator:
    """
    Simulates vision noise for the VSSS system, modifying the environment
    state (specifically, robot and ball positions) in-place.
    
    Supports:
    - Gilbert-Elliott packet dropout per entity.
    - P-G (Poisson-Gaussian) heteroscedastic noise.
    - Outliers (random teleportation within field limits).
    - Domain randomization of parameters.
    """
    def __init__(self, config=None):
        defaults = {
            "pg_noise_enabled": False,
            "pg_noise_std_base": 0.01,
            "pg_noise_std_scale": 0.005,
            "ge_dropout_enabled": False,
            "ge_p": 0.05,
            "ge_q": 0.2,
            "ge_eg": 0.01,
            "ge_eb": 0.9,
            "outlier_enabled": False,
            "outlier_prob": 0.01,
            "outlier_range": 1.0,
            "domain_randomization_enabled": False,
            "pg_noise_std_base_min": 0.001,
            "pg_noise_std_base_max": 0.05,
            "pg_noise_std_scale_min": 0.001,
            "pg_noise_std_scale_max": 0.02,
            "ge_p_min": 0.01,
            "ge_p_max": 0.2,
            "ge_q_min": 0.1,
            "ge_q_max": 0.5,
            "ge_eg_min": 0.0,
            "ge_eg_max": 0.05,
            "ge_eb_min": 0.8,
            "ge_eb_max": 1.0,
            "outlier_prob_min": 0.001,
            "outlier_prob_max": 0.05,
            "outlier_range_min": 0.5,
            "outlier_range_max": 2.0,
            "domain_randomization_interval": 5000,
            "apply_to_ball": True,
            "apply_to_robot_0": True,
            "apply_to_robot_1": True,
            "apply_to_robot_2": True,
        }
        self.config = defaults.copy()
        if config is not None:
            self.config.update(config)
            
        # Internal state tracker for Gilbert-Elliott state ("Good" or "Bad") per entity
        self.states = {}

    def update_config(self, config):
        """
        Updates the active configuration dictionary with new parameters.
        """
        if config is not None:
            self.config.update(config)

    def randomize_domain(self):
        """
        If domain_randomization_enabled is True, updates the active parameters
        by drawing new values uniformly from their respective [min, max] intervals.
        """
        if self.config.get("domain_randomization_enabled", False):
            self.config["pg_noise_std_base"] = random.uniform(
                self.config.get("pg_noise_std_base_min", 0.001),
                self.config.get("pg_noise_std_base_max", 0.05)
            )
            self.config["pg_noise_std_scale"] = random.uniform(
                self.config.get("pg_noise_std_scale_min", 0.001),
                self.config.get("pg_noise_std_scale_max", 0.02)
            )
            self.config["ge_p"] = random.uniform(
                self.config.get("ge_p_min", 0.01),
                self.config.get("ge_p_max", 0.2)
            )
            self.config["ge_q"] = random.uniform(
                self.config.get("ge_q_min", 0.1),
                self.config.get("ge_q_max", 0.5)
            )
            self.config["ge_eg"] = random.uniform(
                self.config.get("ge_eg_min", 0.0),
                self.config.get("ge_eg_max", 0.05)
            )
            self.config["ge_eb"] = random.uniform(
                self.config.get("ge_eb_min", 0.8),
                self.config.get("ge_eb_max", 1.0)
            )
            self.config["outlier_prob"] = random.uniform(
                self.config.get("outlier_prob_min", 0.001),
                self.config.get("outlier_prob_max", 0.05)
            )
            self.config["outlier_range"] = random.uniform(
                self.config.get("outlier_range_min", 0.5),
                self.config.get("outlier_range_max", 2.0)
            )

    def _get_and_transition_state(self, entity_key):
        """
        Updates and returns the Gilbert-Elliott state for the specified entity.
        """
        current_state = self.states.get(entity_key, "Good")
        p = self.config.get("ge_p", 0.05)
        q = self.config.get("ge_q", 0.2)
        
        if current_state == "Good":
            if random.random() < p:
                next_state = "Bad"
            else:
                next_state = "Good"
        else:  # "Bad"
            if random.random() < q:
                next_state = "Good"
            else:
                next_state = "Bad"
                
        self.states[entity_key] = next_state
        return next_state

    def _apply_position_noise(self, entity, environment_msg):
        """
        Applies outlier noise or P-G heteroscedastic noise to the entity's position.
        """
        # Determine limits
        limit_x = self.config.get("outlier_range", 1.0)
        limit_y = self.config.get("outlier_range", 1.0)
        if environment_msg.HasField('field'):
            field = environment_msg.field
            if field.length > 0 and field.width > 0:
                limit_x = field.length / 2.0
                limit_y = field.width / 2.0
                
        # Check outlier
        if self.config.get("outlier_enabled", False) and random.random() < self.config.get("outlier_prob", 0.01):
            entity.x = random.uniform(-limit_x, limit_x)
            entity.y = random.uniform(-limit_y, limit_y)
        else:
            # Check P-G noise
            if self.config.get("pg_noise_enabled", False):
                vx = getattr(entity, 'vx', 0.0)
                vy = getattr(entity, 'vy', 0.0)
                base = self.config.get("pg_noise_std_base", 0.01)
                scale = self.config.get("pg_noise_std_scale", 0.005)
                sigma = base + scale * math.sqrt(vx**2 + vy**2)
                if sigma > 0:
                    entity.x += random.gauss(0, sigma)
                    entity.y += random.gauss(0, sigma)

    def _apply_dict_noise(self, entity_dict):
        """
        Applies noise to a dictionary entity (with pos_x, pos_y).
        """
        limit_x = self.config.get("outlier_range", 1.0)
        limit_y = self.config.get("outlier_range", 1.0)
        
        if self.config.get("outlier_enabled", False) and random.random() < self.config.get("outlier_prob", 0.01):
            entity_dict['pos_x'] = random.uniform(-limit_x, limit_x)
            entity_dict['pos_y'] = random.uniform(-limit_y, limit_y)
        else:
            if self.config.get("pg_noise_enabled", False):
                vx = entity_dict.get('vel_x', 0.0)
                vy = entity_dict.get('vel_y', 0.0)
                base = self.config.get("pg_noise_std_base", 0.01)
                scale = self.config.get("pg_noise_std_scale", 0.005)
                sigma = base + scale * math.sqrt(vx**2 + vy**2)
                if sigma > 0:
                    entity_dict['pos_x'] += random.gauss(0, sigma)
                    entity_dict['pos_y'] += random.gauss(0, sigma)

    def apply_noise(self, environment_msg):
        """
        Modifies the environment_msg in-place to simulate vision noise.
        """
        if isinstance(environment_msg, dict):
            if 'ball' in environment_msg and self.config.get('apply_to_ball', True):
                state = self._get_and_transition_state("ball")
                dropped = False
                if self.config.get("ge_dropout_enabled", False):
                    p_drop = self.config.get("ge_eg", 0.01) if state == "Good" else self.config.get("ge_eb", 0.9)
                    if random.random() < p_drop: dropped = True
                if dropped:
                    environment_msg['ball']['pos_x'] = 10000.0
                    environment_msg['ball']['pos_y'] = 10000.0
                else:
                    self._apply_dict_noise(environment_msg['ball'])
                    
            if 'robots' in environment_msg:
                for robot_id, r in environment_msg['robots'].items():
                    if not self.config.get(f'apply_to_robot_{robot_id}', True): continue
                    state = self._get_and_transition_state(f"robot_{robot_id}")
                    dropped = False
                    if self.config.get("ge_dropout_enabled", False):
                        p_drop = self.config.get("ge_eg", 0.01) if state == "Good" else self.config.get("ge_eb", 0.9)
                        if random.random() < p_drop: dropped = True
                    if dropped:
                        r['pos_x'] = 10000.0
                        r['pos_y'] = 10000.0
                    else:
                        self._apply_dict_noise(r)
            return

        if not hasattr(environment_msg, 'HasField') or not environment_msg.HasField('frame'):
            return
            
        frame = environment_msg.frame
        
        # 1. Apply to Ball
        if frame.HasField('ball') and self.config.get('apply_to_ball', True):
            entity_key = "ball"
            state = self._get_and_transition_state(entity_key)
            dropped = False
            if self.config.get("ge_dropout_enabled", False):
                p_drop = self.config.get("ge_eg", 0.01) if state == "Good" else self.config.get("ge_eb", 0.9)
                if random.random() < p_drop:
                    dropped = True
                    
            if dropped:
                frame.ClearField('ball')
            else:
                self._apply_position_noise(frame.ball, environment_msg)
                
        # 2. Apply to Yellow robots
        robots_yellow_kept = []
        for robot in frame.robots_yellow:
            if not self.config.get(f'apply_to_robot_{robot.robot_id}', True):
                robots_yellow_kept.append(robot)
                continue
            entity_key = f"yellow_{robot.robot_id}"
            state = self._get_and_transition_state(entity_key)
            dropped = False
            if self.config.get("ge_dropout_enabled", False):
                p_drop = self.config.get("ge_eg", 0.01) if state == "Good" else self.config.get("ge_eb", 0.9)
                if random.random() < p_drop:
                    dropped = True
                    
            if not dropped:
                robot_copy = type(robot)()
                robot_copy.CopyFrom(robot)
                self._apply_position_noise(robot_copy, environment_msg)
                robots_yellow_kept.append(robot_copy)
                
        frame.ClearField('robots_yellow')
        for r in robots_yellow_kept:
            frame.robots_yellow.add().CopyFrom(r)
            
        # 3. Apply to Blue robots
        robots_blue_kept = []
        for robot in frame.robots_blue:
            entity_key = f"blue_{robot.robot_id}"
            state = self._get_and_transition_state(entity_key)
            dropped = False
            if self.config.get("ge_dropout_enabled", False):
                p_drop = self.config.get("ge_eg", 0.01) if state == "Good" else self.config.get("ge_eb", 0.9)
                if random.random() < p_drop:
                    dropped = True
                    
            if not dropped:
                robot_copy = type(robot)()
                robot_copy.CopyFrom(robot)
                self._apply_position_noise(robot_copy, environment_msg)
                robots_blue_kept.append(robot_copy)
                
        frame.ClearField('robots_blue')
        for r in robots_blue_kept:
            frame.robots_blue.add().CopyFrom(r)
