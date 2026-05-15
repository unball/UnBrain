import json
from dataclasses import asdict
from typing import Optional
from .predictor import Cmd, Frame

class JSONLLogger:
    """Escreve linhas JSONL simples para frames e comandos."""
    def __init__(self, frames_path: str, cmds_path: str):
        self.frames_path = frames_path
        self.cmds_path = cmds_path
        self._f_frames = open(frames_path, "a", buffering=1)
        self._f_cmds = open(cmds_path, "a", buffering=1)

    def log_frame(self, robot_id: int, fr: Frame):
        obj = {"robot_id": robot_id, **asdict(fr)}
        self._f_frames.write(json.dumps(obj) + "\n")

    def log_cmd(self, robot_id: int, cmd: Cmd):
        obj = {"robot_id": robot_id, **asdict(cmd)}
        self._f_cmds.write(json.dumps(obj) + "\n")

    def close(self):
        try:
            self._f_frames.close()
        finally:
            self._f_cmds.close()
