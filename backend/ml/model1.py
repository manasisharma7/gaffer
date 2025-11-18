# model1.py - Dynamic Tactical Shape Analysis (5-minute window)
# Uses model0_load_data.py for loading

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.spatial import ConvexHull
from ml.model0_load_data import load_tracking, load_match_metadata


FPS = 25  # SkillCorner default

# ------------------------------------------------
# Select valid frames and limit to first N minutes
# ------------------------------------------------
def select_valid_frames(frames, n_minutes=5):
    valid_frames = [f for f in frames if f.get("player_data") and len(f["player_data"]) > 0]
    max_frames = int(n_minutes * 60 * FPS)
    return valid_frames[:max_frames]

# ------------------------------------------------
# Team Compactness (Convex Hull area)
# ------------------------------------------------
# ------------------------------------------------
# Team Compactness (Convex Hull area)
# ------------------------------------------------
def compute_team_compactness(frames, team_id=None):
    compactness = []

    for f in frames:
        # Use all players, ignore team_id if not present
        players = [[p["x"], p["y"]] for p in f["player_data"] if p.get("x") is not None]

        if len(players) < 3:
            compactness.append(np.nan)
            continue

        try:
            hull = ConvexHull(np.array(players))
            compactness.append(hull.area)
        except:
            compactness.append(np.nan)

    return compactness


# ------------------------------------------------
# Defensive Line Height
# ------------------------------------------------
def compute_defensive_line_height(frames, team_id=None):
    heights = []

    for f in frames:
        # Use all players, ignore team_id
        players = [p for p in f["player_data"] if p.get("x") is not None]

        if len(players) == 0:
            heights.append(np.nan)
            continue

        players_sorted = sorted(players, key=lambda p: p["x"])
        def_line = players_sorted[:4]  # take first 4 as defensive line
        avg_y = np.mean([p["y"] for p in def_line]) if def_line else np.nan
        heights.append(avg_y)

    return heights


# ------------------------------------------------
# Plotting
# ------------------------------------------------
def plot_metric(metric, title, save_path):
    plt.figure(figsize=(10, 4))
    plt.plot(metric, linewidth=2)
    plt.title(title)
    plt.xlabel("Frame")
    plt.ylabel(title)
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()

# ------------------------------------------------
# Main Runner
# ------------------------------------------------
def run_model1(frames, meta, out_dir, n_minutes=5):
    out_dir.mkdir(parents=True, exist_ok=True)

    frames = select_valid_frames(frames, n_minutes)
    print(f"Using {len(frames)} valid frames.")

    teamA = meta["home_team"]["id"]
    teamB = meta["away_team"]["id"]

    print("Computing compactness...")
    compA = compute_team_compactness(frames, teamA)
    compB = compute_team_compactness(frames, teamB)

    plot_metric(compA, f"Team {teamA} Compactness", out_dir / "compactness_A.png")
    plot_metric(compB, f"Team {teamB} Compactness", out_dir / "compactness_B.png")

    print("Computing defensive line height...")
    dlA = compute_defensive_line_height(frames, teamA)
    dlB = compute_defensive_line_height(frames, teamB)

    plot_metric(dlA, f"Team {teamA} Defensive Line Height", out_dir / "def_line_A.png")
    plot_metric(dlB, f"Team {teamB} Defensive Line Height", out_dir / "def_line_B.png")

    print("Model 1 complete! Outputs saved in:", out_dir)

# ------------------------------------------------
# CLI
# ------------------------------------------------
if __name__ == "__main__":
    frames = load_tracking()
    meta = load_match_metadata()
    OUTPUT = Path("model1_output")
    run_model1(frames, meta, OUTPUT, n_minutes=5)
