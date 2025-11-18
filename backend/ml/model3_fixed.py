# model3_fixed.py - Pitch Control Heatmap (Working)
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from ml.model0_load_data import load_tracking, load_match_metadata


FPS = 25
FIELD_X = (-52.5, 52.5)  # meters
FIELD_Y = (-34, 34)      # meters

# ------------------------------------------------
# Helpers
# ------------------------------------------------
def select_valid_frames(frames, n_minutes=5):
    max_frames = int(n_minutes * 60 * FPS)
    valid_frames = [f for f in frames if f.get("player_data") and len(f["player_data"]) > 0]
    return valid_frames[:max_frames]

def map_players_to_teams(frames, meta):
    """Map player IDs to home/away sets without relying on metadata players."""
    all_players = set()
    for f in frames:
        for p in f.get("player_data", []):
            pid = p.get("player_id")
            if pid is not None:
                all_players.add(pid)
    all_players = list(all_players)
    mid = len(all_players) // 2
    home_players = set(all_players[:mid])
    away_players = set(all_players[mid:])
    return home_players, away_players

def compute_pitch_control(frames, home_players, away_players, grid_size=(50, 50)):
    """Simple pitch control approximation: count presence in grid."""
    x_bins = np.linspace(FIELD_X[0], FIELD_X[1], grid_size[0])
    y_bins = np.linspace(FIELD_Y[0], FIELD_Y[1], grid_size[1])
    pc_home = np.zeros(grid_size)
    pc_away = np.zeros(grid_size)

    for f in frames:
        for p in f.get("player_data", []):
            pid = p.get("player_id")
            x, y = p.get("x"), p.get("y")
            if x is None or y is None or pid is None:
                continue
            xi = np.digitize(x, x_bins) - 1
            yi = np.digitize(y, y_bins) - 1
            xi = np.clip(xi, 0, grid_size[0]-1)
            yi = np.clip(yi, 0, grid_size[1]-1)
            if pid in home_players:
                pc_home[xi, yi] += 1
            else:
                pc_away[xi, yi] += 1

    # Normalize to 0-1
    pc_sum = pc_home / (pc_home + pc_away + 1e-6)  # fraction controlled by home
    return pc_sum.T  # transpose for plotting

def plot_pitch_control(pc_grid, save_path):
    plt.figure(figsize=(12, 8))
    plt.imshow(pc_grid, origin='lower', extent=(FIELD_X[0], FIELD_X[1], FIELD_Y[0], FIELD_Y[1]),
               cmap='coolwarm', vmin=0, vmax=1, aspect='auto')
    plt.colorbar(label='Pitch Control (Home Team)')
    plt.title("Pitch Control Heatmap")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Pitch Control heatmap saved: {save_path}")

# ------------------------------------------------
# Main Runner
# ------------------------------------------------
def run_model3(frames, meta, out_dir, n_minutes=5):
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = select_valid_frames(frames, n_minutes)
    print(f"Using {len(frames)} valid frames for pitch control.")

    home_players, away_players = map_players_to_teams(frames, meta)
    pc_grid = compute_pitch_control(frames, home_players, away_players)
    plot_pitch_control(pc_grid, out_dir / "pitch_control.png")

    print("Model 3 complete! Outputs saved in:", out_dir)

# ------------------------------------------------
# CLI
# ------------------------------------------------
if __name__ == "__main__":
    frames = load_tracking()
    meta = load_match_metadata()
    OUTPUT = Path("model3_output_fixed")
    run_model3(frames, meta, OUTPUT)
