# pyrefly: ignore [missing-import]
import gymnasium as gym
# pyrefly: ignore [missing-import]
from tools.vision_noise import VisionNoiseSimulator

class MockMessage:
    def __init__(self, frame, field):
        self.frame = frame
        self.field = field
    def HasField(self, name):
        return True

class MockFrameWrapper:
    def __init__(self, rsoccer_frame):
        self._frame = rsoccer_frame
    
    def HasField(self, name):
        if name == 'ball': return hasattr(self._frame, 'ball') and self._frame.ball is not None
        if name == 'robots_yellow': return hasattr(self._frame, 'robots_yellow')
        if name == 'robots_blue': return hasattr(self._frame, 'robots_blue')
        return False
        
    def ClearField(self, name):
        # Removemos o OUT_OF_BOUNDS = 1.6
        # Agora simulamos um tracking real: se a câmera falha, 
        # a posição congela no último frame e a velocidade zera.
        
        if name == 'ball':
            # Mantém self._frame.ball.x e y como estavam
            if hasattr(self._frame.ball, 'v_x'): self._frame.ball.v_x = 0.0
            if hasattr(self._frame.ball, 'v_y'): self._frame.ball.v_y = 0.0
            
        elif name == 'robots_yellow':
            iterable = self._frame.robots_yellow.values() if isinstance(self._frame.robots_yellow, dict) else self._frame.robots_yellow
            for r in iterable:
                if hasattr(r, 'v_x'): r.v_x = 0.0
                if hasattr(r, 'v_y'): r.v_y = 0.0
                if hasattr(r, 'v_theta'): r.v_theta = 0.0
                
        elif name == 'robots_blue':
            iterable = self._frame.robots_blue.values() if isinstance(self._frame.robots_blue, dict) else self._frame.robots_blue
            for r in iterable:
                if hasattr(r, 'v_x'): r.v_x = 0.0
                if hasattr(r, 'v_y'): r.v_y = 0.0
                if hasattr(r, 'v_theta'): r.v_theta = 0.0   

    @property
    def ball(self):
        return self._frame.ball
        
    @property
    def robots_yellow(self):
        self._yellow_list = MockRobotList(self._frame.robots_yellow)
        return self._yellow_list
        
    @property
    def robots_blue(self):
        self._blue_list = MockRobotList(self._frame.robots_blue)
        return self._blue_list

    def apply_real_updates(self):
        if hasattr(self, '_yellow_list'):
            self._yellow_list.update_real()
        if hasattr(self, '_blue_list'):
            self._blue_list.update_real()

class MockRobot:
    def __init__(self, real_robot=None, robot_id=0):
        self._real = real_robot
        self.robot_id = robot_id
        self.x = getattr(real_robot, 'x', 0.0) if real_robot else 0.0
        self.y = getattr(real_robot, 'y', 0.0) if real_robot else 0.0
        self.theta = getattr(real_robot, 'theta', 0.0) if real_robot else 0.0
        self.v_x = getattr(real_robot, 'v_x', 0.0) if real_robot else 0.0
        self.v_y = getattr(real_robot, 'v_y', 0.0) if real_robot else 0.0
        self.v_theta = getattr(real_robot, 'v_theta', 0.0) if real_robot else 0.0

    def CopyFrom(self, other):
        self.x = getattr(other, 'x', 0.0)
        self.y = getattr(other, 'y', 0.0)
        self.theta = getattr(other, 'theta', 0.0)
        self.v_x = getattr(other, 'v_x', 0.0)
        self.v_y = getattr(other, 'v_y', 0.0)
        self.v_theta = getattr(other, 'v_theta', 0.0)
        self.robot_id = getattr(other, 'robot_id', self.robot_id)

    def update_real(self):
        if self._real is not None:
            self._real.x = self.x
            self._real.y = self.y
            if hasattr(self._real, 'theta'): self._real.theta = self.theta
            if hasattr(self._real, 'v_x'): self._real.v_x = self.v_x
            if hasattr(self._real, 'v_y'): self._real.v_y = self.v_y
            if hasattr(self._real, 'v_theta'): self._real.v_theta = self.v_theta

class MockRobotList:
    def __init__(self, rsoccer_robots):
        self.rsoccer_robots = rsoccer_robots
        self.mocks = []
        iterable = rsoccer_robots.items() if isinstance(rsoccer_robots, dict) else enumerate(rsoccer_robots)
        for i, r in iterable:
            self.mocks.append(MockRobot(r, i))
    def __iter__(self):
        return iter(self.mocks)
    def add(self):
        m = MockRobot(type('Dummy', (object,), {'x': 0, 'y': 0})(), 0)
        self.mocks.append(m)
        return m
    def update_real(self):
        for m in self.mocks:
            m.update_real()

    # The following properties belong to MockFrameWrapper, which was opened at line 11
    # We must patch MockFrameWrapper explicitly.

class MockFieldWrapper:
    def __init__(self):
        self.length = 1.5
        self.width = 1.3

class VisionNoiseGymWrapper(gym.Wrapper):
    def __init__(self, env, config=None):
        super().__init__(env)
        self.noise_sim = VisionNoiseSimulator(config)
        self.noise_frame_counter = 0

    def step(self, action, *args, **kwargs):
        # 1. Obter a observação e as infos do ambiente original
        obs, reward, terminated, truncated, info = self.env.step(action, *args, **kwargs)
        
        # Domain Randomization update
        if self.noise_sim.config.get("domain_randomization_enabled", False):
            self.noise_frame_counter += 1
            if self.noise_frame_counter >= self.noise_sim.config.get("domain_randomization_interval", 5000):
                self.noise_sim.randomize_domain()
                self.noise_frame_counter = 0
        
        # Aplica o ruído no `self.env.unwrapped.frame` original
        if hasattr(self.env.unwrapped, 'frame'):
            msg = MockMessage(MockFrameWrapper(self.env.unwrapped.frame), MockFieldWrapper())
            
            # --- 1. SALVAR O ESTADO REAL E PERFEITO ---
            old_ball_x, old_ball_y = self.env.unwrapped.frame.ball.x, self.env.unwrapped.frame.ball.y
            old_ball_vx = getattr(self.env.unwrapped.frame.ball, 'v_x', 0.0)
            old_ball_vy = getattr(self.env.unwrapped.frame.ball, 'v_y', 0.0)
            
            old_robots_state = {}
            
            iterable_yellow = self.env.unwrapped.frame.robots_yellow.values() if isinstance(self.env.unwrapped.frame.robots_yellow, dict) else self.env.unwrapped.frame.robots_yellow
            for i, r in enumerate(iterable_yellow): 
                old_robots_state[f"y{i}"] = {
                    'x': r.x, 'y': r.y, 
                    'theta': getattr(r, 'theta', 0.0),
                    'v_x': getattr(r, 'v_x', 0.0),
                    'v_y': getattr(r, 'v_y', 0.0),
                    'v_theta': getattr(r, 'v_theta', 0.0)
                }
                
            iterable_blue = self.env.unwrapped.frame.robots_blue.values() if isinstance(self.env.unwrapped.frame.robots_blue, dict) else self.env.unwrapped.frame.robots_blue
            for i, r in enumerate(iterable_blue): 
                old_robots_state[f"b{i}"] = {
                    'x': r.x, 'y': r.y, 
                    'theta': getattr(r, 'theta', 0.0),
                    'v_x': getattr(r, 'v_x', 0.0),
                    'v_y': getattr(r, 'v_y', 0.0),
                    'v_theta': getattr(r, 'v_theta', 0.0)
                }
            
            # --- 2. APLICAR O RUÍDO ---
            self.noise_sim.apply_noise(msg)
            msg.frame.apply_real_updates()
            
            # Extrai observação vista pela "câmera falha"
            noisy_obs = self.env.unwrapped._frame_to_observations()
            
            # --- 3. RESTAURAR O ESTADO REAL E PERFEITO DA FÍSICA ---
            self.env.unwrapped.frame.ball.x, self.env.unwrapped.frame.ball.y = old_ball_x, old_ball_y
            if hasattr(self.env.unwrapped.frame.ball, 'v_x'): self.env.unwrapped.frame.ball.v_x = old_ball_vx
            if hasattr(self.env.unwrapped.frame.ball, 'v_y'): self.env.unwrapped.frame.ball.v_y = old_ball_vy
            
            for i, r in enumerate(iterable_yellow): 
                state = old_robots_state[f"y{i}"]
                r.x, r.y = state['x'], state['y']
                if hasattr(r, 'theta'): r.theta = state['theta']
                if hasattr(r, 'v_x'): r.v_x = state['v_x']
                if hasattr(r, 'v_y'): r.v_y = state['v_y']
                if hasattr(r, 'v_theta'): r.v_theta = state['v_theta']
                
            for i, r in enumerate(iterable_blue): 
                state = old_robots_state[f"b{i}"]
                r.x, r.y = state['x'], state['y']
                if hasattr(r, 'theta'): r.theta = state['theta']
                if hasattr(r, 'v_x'): r.v_x = state['v_x']
                if hasattr(r, 'v_y'): r.v_y = state['v_y']
                if hasattr(r, 'v_theta'): r.v_theta = state['v_theta']
            
            return noisy_obs, reward, terminated, truncated, info

        return obs, reward, terminated, truncated, info
