import argparse
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from .dataset import make_dataset
from .models import ResidualMLP

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--cmds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tau_act", type=float, default=0.02)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    args = ap.parse_args()

    X, Y = make_dataset(args.frames, args.cmds, tau_act=args.tau_act)
    ds = TensorDataset(torch.from_numpy(X), torch.from_numpy(Y))
    dl = DataLoader(ds, batch_size=args.batch, shuffle=True, drop_last=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ResidualMLP().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()

    model.train()
    for ep in range(1, args.epochs + 1):
        tot = 0.0
        for xb, yb in dl:
            xb = xb.to(device)
            yb = yb.to(device)
            pred = model(xb)
            loss = loss_fn(pred, yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += float(loss.item()) * xb.size(0)
        print(f"epoch {ep:03d} | loss={tot/len(ds):.6f}")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    torch.save(model.state_dict(), args.out)
    print("saved:", args.out)

if __name__ == "__main__":
    main()
