import json
import os
from dataclasses import asdict
from typing import Optional
from .predictor import Cmd, Frame, BallFrame

class JSONLLogger:
    """Escreve linhas JSONL simples para frames, comandos e bola."""
    def __init__(self, mode: str = "firasim", output_dir: str = "src/state_predictor_project/dataset", clear_old: bool = False):
        os.makedirs(output_dir, exist_ok=True)
        self.frames_path = os.path.join(output_dir, f"dataset_{mode}_frames.jsonl")
        self.cmds_path = os.path.join(output_dir, f"dataset_{mode}_cmds.jsonl")
        self.ball_path = os.path.join(output_dir, f"dataset_{mode}_ball.jsonl")
        
        file_mode = "w" if clear_old else "a"
        self._f_frames = open(self.frames_path, file_mode, buffering=1)
        self._f_cmds = open(self.cmds_path, file_mode, buffering=1)
        self._f_ball = open(self.ball_path, file_mode, buffering=1)

    def log_frame(self, robot_id: int, fr: Frame):
        obj = {"robot_id": robot_id, **asdict(fr)}
        self._f_frames.write(json.dumps(obj) + "\n")
        
    def log_ball_frame(self, fr: BallFrame):
        obj = asdict(fr)
        self._f_ball.write(json.dumps(obj) + "\n")

    def log_cmd(self, robot_id: int, cmd: Cmd):
        obj = {"robot_id": robot_id, **asdict(cmd)}
        self._f_cmds.write(json.dumps(obj) + "\n")

    def close(self):
        try:
            self._f_frames.close()
            self._f_ball.close()
        finally:
            self._f_cmds.close()
