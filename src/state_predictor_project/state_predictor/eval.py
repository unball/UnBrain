import argparse
import numpy as np
import torch
from .dataset import make_dataset
from .models import ResidualMLP

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--cmds", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--tau_act", type=float, default=0.02)
    args = ap.parse_args()

    X, Y = make_dataset(args.frames, args.cmds, tau_act=args.tau_act)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ResidualMLP().to(device)
    model.load_state_dict(torch.load(args.model, map_location=device))
    model.eval()

    with torch.no_grad():
        pred = model(torch.from_numpy(X).to(device)).cpu().numpy()

    mse = np.mean((pred - Y) ** 2)
    print("MSE residual:", mse)

if __name__ == "__main__":
    main()
