import copy
import os
import queue
import time
from typing import Iterable, Optional, Tuple

import numpy as np

from .state_predictor.logging import JSONLLogger
from .state_predictor.predictor import (
    BallFrame,
    Cmd,
    CommandLogger,
    Frame,
    FrameLogger,
    StatePredictor,
    torch,
)


class VisionInterceptor:
    """Queues vision frames and optionally replaces team robot poses with predictions."""

    def __init__(
        self,
        inject_delay: float = 0.0,
        lookahead: float = 0.05,
        mode: str = "firasim",
        disable_ai: bool = False,
        record: bool = False,
    ):
        self.inject_delay = max(0.0, float(inject_delay))
        self.lookahead = float(lookahead)
        self.mode = mode
        self.disable_ai = disable_ai
        self.record = record
        self.active = False

        self.frames = queue.Queue()
        self.cmd_logger = CommandLogger()
        self.frame_logger = FrameLogger()
        self.logger = JSONLLogger(mode=mode) if record else None

        model_path = os.path.join(
            os.path.dirname(__file__),
            "state_predictor",
            f"{mode}_residual_model.pth",
        )
        use_residual = (not disable_ai) and torch is not None and os.path.exists(model_path)
        self.predictor = StatePredictor(
            self.cmd_logger,
            self.frame_logger,
            use_residual=use_residual,
            model_path=model_path if use_residual else None,
        )

        self.mse_sum = 0.0
        self.mse_count = 0
        self.raw_poses = {}

    def set_active(self, active: bool):
        self.active = bool(active)

    def set_record_state(self, state: bool):
        self.record = bool(state)
        if self.record and self.logger is None:
            self.logger = JSONLLogger(mode=self.mode)
        elif not self.record and self.logger is not None:
            if hasattr(self.logger, "close"):
                self.logger.close()
            self.logger = None

    def enqueue_frame(self, message):
        self.frames.put((time.monotonic(), message))

    def dequeue_ready_frame(self):
        if self.frames.empty():
            return None

        ready_frame = None
        # Drena todos os frames que já passaram do inject_delay (Esvazia o buffer de passado)
        while not self.frames.empty():
            item = self.frames.queue[0]
            if time.monotonic() - item[0] < self.inject_delay:
                break
            ready_frame = self.frames.get()
            
        return ready_frame

    def dequeue_ready_frames(self):
        """Drena e retorna todos os frames que já passaram do delay."""
        if self.frames.empty():
            return []
            
        ready_frames = []
        while not self.frames.empty():
            item = self.frames.queue[0]
            if time.monotonic() - item[0] < self.inject_delay:
                break
            ready_frames.append(self.frames.get())
            
        return ready_frames

    def push_cmd(self, robot_id: int, v: float, w: float, t: Optional[float] = None):
        t_cmd = time.monotonic() if t is None else float(t)
        self.cmd_logger.push(int(robot_id), float(v), float(w), t_cmd)
        if self.logger is not None:
            self.logger.log_cmd(int(robot_id), Cmd(t=t_cmd, v=float(v), w=float(w)))

    def intercept_and_predict(
        self,
        message,
        t_frame: float,
        team_yellow: bool,
        n_robots: Iterable[int],
        alpha: float = 1.0,
    ):
        self._capture_frame(message, t_frame, team_yellow, n_robots)
        if not self.active:
            return message

        t_now = time.monotonic()
        for robot_id in n_robots:
            robot = self._get_team_robot(message, robot_id, team_yellow)
            pose = self._robot_pose(robot)
            if pose is None:
                continue

            # Store the raw pose before any modification
            self.raw_poses[(team_yellow, int(robot_id))] = pose

            if self.disable_ai:
                continue

            pred = self.predictor.estimate_now(int(robot_id), t_now, self.lookahead)
            if pred is None:
                continue

            blended = (1.0 - alpha) * np.array(pose, dtype=np.float32) + alpha * pred
            self._set_robot_pose(robot, blended)

            err = float(np.mean((pred[:2] - np.array(pose[:2], dtype=np.float32)) ** 2))
            self.mse_sum += err
            self.mse_count += 1

        return message

    def _capture_frame(self, message, t_frame: float, team_yellow: bool, n_robots: Iterable[int]):
        for robot_id in n_robots:
            robot = self._get_team_robot(message, robot_id, team_yellow)
            pose = self._robot_pose(robot)
            if pose is None:
                continue
            fr = Frame(t=t_frame, x=pose[0], y=pose[1], th=pose[2])
            self.frame_logger.push(int(robot_id), fr.x, fr.y, fr.th, fr.t)
            if self.logger is not None:
                self.logger.log_frame(int(robot_id), fr)

        ball = self._ball_frame(message, t_frame)
        if ball is not None:
            self.frame_logger.push_ball(ball.x, ball.y, ball.vx, ball.vy, ball.t)
            if self.logger is not None:
                self.logger.log_ball_frame(ball)

    def _get_team_robot(self, message, robot_id: int, team_yellow: bool):
        if isinstance(message, dict):
            robots = message.get("robots", {})
            return robots.get(robot_id) or robots.get(str(robot_id))

        frame = getattr(message, "frame", None)
        if frame is None:
            detection = getattr(message, "detection", None)
            robots = getattr(detection, "robots_yellow" if team_yellow else "robots_blue", None)
        else:
            robots = getattr(frame, "robots_yellow" if team_yellow else "robots_blue", None)

        if robots is None or robot_id >= len(robots):
            return None
        return robots[robot_id]

    def _robot_pose(self, robot) -> Optional[Tuple[float, float, float]]:
        if robot is None:
            return None
        if isinstance(robot, dict):
            if not all(k in robot for k in ("pos_x", "pos_y", "th")):
                return None
            return float(robot["pos_x"]), float(robot["pos_y"]), float(robot["th"])
        if not all(hasattr(robot, k) for k in ("x", "y", "orientation")):
            return None
        return float(robot.x), float(robot.y), float(robot.orientation)

    def _set_robot_pose(self, robot, pose):
        if isinstance(robot, dict):
            robot["pos_x"], robot["pos_y"], robot["th"] = map(float, pose[:3])
            return

        robot.x = float(pose[0])
        robot.y = float(pose[1])
        robot.orientation = float(pose[2])
        robot.x = float(pose[0])
        robot.y = float(pose[1])
        robot.orientation = float(pose[2])

    def _ball_frame(self, message, t_frame: float):
        if isinstance(message, dict):
            ball = message.get("ball")
            if not ball:
                return None
            return BallFrame(
                t=t_frame,
                x=float(ball.get("pos_x", 0.0)),
                y=float(ball.get("pos_y", 0.0)),
                vx=float(ball.get("vel_x", 0.0)),
                vy=float(ball.get("vel_y", 0.0)),
            )

        frame = getattr(message, "frame", None)
        ball = getattr(frame, "ball", None) if frame is not None else None
        if ball is None:
            detection = getattr(message, "detection", None)
            balls = getattr(detection, "balls", None)
            if balls:
                ball = balls[0]
        if ball is None:
            return None

        scale = 1000.0 if abs(float(getattr(ball, "x", 0.0))) > 10 else 1.0
        return BallFrame(
            t=t_frame,
            x=float(getattr(ball, "x", 0.0)) / scale,
            y=float(getattr(ball, "y", 0.0)) / scale,
            vx=float(getattr(ball, "vx", 0.0)) / scale,
            vy=float(getattr(ball, "vy", 0.0)) / scale,
        )

    def get_raw_pose(self, team_yellow: bool, robot_id: int):
        return self.raw_poses.get((team_yellow, robot_id))
