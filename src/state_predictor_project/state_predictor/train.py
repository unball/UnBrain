import argparse
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split

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
    # Criar TensorDataset
    ds = TensorDataset(torch.from_numpy(X), torch.from_numpy(Y))
    
    # Validation Split (80% train, 20% validation)
    val_size = int(len(ds) * 0.2)
    train_size = len(ds) - val_size
    train_ds, val_ds = random_split(ds, [train_size, val_size], generator=torch.Generator().manual_seed(42))
    
    # Criar DataLoaders independentes
    train_dl = DataLoader(train_ds, batch_size=args.batch, shuffle=True, drop_last=True)
    val_dl = DataLoader(val_ds, batch_size=args.batch, shuffle=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ResidualMLP().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()

    best_val_loss = float('inf')
    patience = 15
    patience_counter = 0

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    for ep in range(1, args.epochs + 1):
        # Fase de Treinamento
        model.train()
        train_loss_sum = 0.0
        for xb, yb in train_dl:
            xb = xb.to(device)
            yb = yb.to(device)
            pred = model(xb)
            loss = loss_fn(pred, yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            train_loss_sum += float(loss.item()) * xb.size(0)
        
        train_loss = train_loss_sum / len(train_ds)

        # Fase de Validação (Prova Surpresa)
        model.eval()
        val_loss_sum = 0.0
        with torch.no_grad():
            for xb, yb in val_dl:
                xb = xb.to(device)
                yb = yb.to(device)
                pred = model(xb)
                loss = loss_fn(pred, yb)
                val_loss_sum += float(loss.item()) * xb.size(0)
        
        val_loss = val_loss_sum / len(val_ds) if len(val_ds) > 0 else 0.0

        print(f"epoch {ep:03d} | train_loss={train_loss:.6f} | val_loss={val_loss:.6f}")

        # Lógica de Early Stopping e salvamento do modelo
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), args.out)
            # print(f"  --> Melhor modelo salvo (val_loss={val_loss:.6f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping na época {ep}. O modelo já começou a sofrer overfitting.")
                break

    print("Treinamento finalizado. Melhor modelo salvo em:", args.out)

if __name__ == "__main__":
    main()
