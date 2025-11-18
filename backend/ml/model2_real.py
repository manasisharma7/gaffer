# model2_team_split.py
"""
Model 2 (team split)
- Computes total distance and high-intensity sprint time per player for the full match (n_minutes=None)
- Splits metrics by team (home vs away) using match metadata when available
- Saves per-team plots and JSON summaries
"""
import matplotlib
matplotlib.use("Agg")   # disable GUI backend

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
import re
from typing import List, Dict, Tuple, Optional, Any

from ml.model0_load_data import load_tracking, load_match_metadata

# Config
FPS = 25
HIGH_INTENSITY_THRESHOLD = 5.0
OUTPUT = Path("model2_output_team")
OUTPUT.mkdir(parents=True, exist_ok=True)


# --- Helper to sanitize team names so Windows does not crash ---
def clean_team_name(name):
    if isinstance(name, dict):
        # If metadata has full team object
        name = name.get("_name") or name.get("name") or name.get("short_name") or "Team"
    name = str(name)
    return re.sub(r"[^A-Za-z0-9]+", "_", name)  # Replace invalid characters with underscore


# --- Helpers for tolerant extraction of id/x/y/team/name from frames ---
def extract_player_fields(p: dict) -> Tuple[Optional[Any], Optional[float], Optional[float], Optional[str]]:
    pid = None
    for k in ("player_id", "id", "pid", "playerId"):
        if k in p and p[k] is not None:
            pid = p[k]; break

    x = None; y = None
    for k in ("x","X","pos_x","posX","x_world","x_pos"):
        if k in p and p[k] is not None:
            x = p[k]; break
    for k in ("y","Y","pos_y","posY","y_world","y_pos"):
        if k in p and p[k] is not None:
            y = p[k]; break
    if (x is None or y is None) and isinstance(p.get("position"), dict):
        pos = p["position"]
        if x is None:
            for k in ("x","pos_x","x_world"):
                if k in pos and pos[k] is not None:
                    x = pos[k]; break
        if y is None:
            for k in ("y","pos_y","y_world"):
                if k in pos and pos[k] is not None:
                    y = pos[k]; break

    team_label = None
    for k in ("team","side","team_id","teamName"):
        if k in p and p[k] is not None:
            team_label = p[k]; break

    try: x = float(x) if x is not None else None
    except: x = None
    try: y = float(y) if y is not None else None
    except: y = None

    return pid, x, y, team_label


def map_meta_player_names(meta: dict) -> Dict[Any, str]:
    name_map = {}
    players_list = meta.get("players") or meta.get("team_players") or None
    if isinstance(players_list, list):
        for p in players_list:
            pid = p.get("player_id") or p.get("id") or p.get("pid")
            name = p.get("name") or p.get("player_name") or p.get("display_name")
            if pid is None and (p.get("first_name") or p.get("last_name")):
                name = " ".join(filter(None, [p.get("first_name"), p.get("last_name")]))
            if pid is not None and name:
                name_map[pid] = name
    for team_key in ("home", "home_team", "home_team_players", "home_team_roster"):
        team_entry = meta.get(team_key)
        if isinstance(team_entry, dict):
            tplayers = team_entry.get("players") if isinstance(team_entry.get("players"), list) else team_entry.get("squad")
            if isinstance(tplayers, list):
                for p in tplayers:
                    pid = p.get("player_id") or p.get("id") or p.get("pid")
                    name = p.get("name") or p.get("player_name")
                    if pid is not None and name:
                        name_map[pid] = name
    return name_map


# --- Core calculation ---
def compute_distances_and_sprints(frames: List[dict], fps: int) -> Tuple[Dict[Any,float], Dict[Any,int], Dict[Any,str]]:
    dt = 1.0 / fps
    last_pos = {}
    distances = {}
    sprints = {}
    pid_team = {}

    for frame in frames:
        pd = frame.get("player_data", []) or frame.get("players", []) or []
        for p in pd:
            pid, x, y, team_label = extract_player_fields(p)
            if pid is None or x is None or y is None:
                continue
            try: pid_key = int(pid)
            except: pid_key = pid
            if team_label is not None and pid_key not in pid_team:
                pid_team[pid_key] = team_label

            if pid_key in last_pos:
                dx = x - last_pos[pid_key][0]
                dy = y - last_pos[pid_key][1]
                dist = np.hypot(dx, dy)
                distances[pid_key] = distances.get(pid_key, 0.0) + float(dist)
                if dist / dt >= HIGH_INTENSITY_THRESHOLD:
                    sprints[pid_key] = sprints.get(pid_key, 0) + 1
            else:
                distances.setdefault(pid_key, 0.0)
                sprints.setdefault(pid_key, 0)

            last_pos[pid_key] = (x, y)

    return distances, sprints, pid_team


# --- Main Runner ---
def run(n_minutes: Optional[float] = None):
    frames = load_tracking()
    meta = load_match_metadata() or {}

    fps_meta = None
    for k in ("fps","frame_rate","frameRate","sample_rate"):
        if meta.get(k):
            try: fps_meta = int(meta.get(k)); break
            except: pass
    fps_use = fps_meta or FPS
    print(f"Using FPS = {fps_use}")

    valid_frames = frames if n_minutes is None else frames[: int(n_minutes * 60 * fps_use)]
    if len(valid_frames) == 0:
        raise RuntimeError("No valid frames found. Check your tracking loader output.")

    distances, sprint_frames, pid_team_map_from_frames = compute_distances_and_sprints(valid_frames, fps_use)
    sprint_seconds = {pid: int(frames_count) * (1.0 / fps_use) for pid, frames_count in sprint_frames.items()}

    home_name_raw = meta.get("home_team") or meta.get("home_name") or meta.get("home") or "TeamA"
    away_name_raw = meta.get("away_team") or meta.get("away_name") or meta.get("away") or "TeamB"

    home_name = clean_team_name(home_name_raw)
    away_name = clean_team_name(away_name_raw)

    id_to_name = map_meta_player_names(meta)

    home_ids = meta.get("home_players") or meta.get("home_team_player_ids") or meta.get("home_squad") or []
    away_ids = meta.get("away_players") or meta.get("away_team_player_ids") or meta.get("away_squad") or []

    def try_int_list(lst):
        out = []
        for v in lst or []:
            try: out.append(int(v))
            except: out.append(v)
        return out

    home_ids = try_int_list(home_ids)
    away_ids = try_int_list(away_ids)

    pid_to_team = {}
    for pid in home_ids: pid_to_team[pid] = "A"
    for pid in away_ids: pid_to_team[pid] = "B"

    for pid, label in pid_team_map_from_frames.items():
        if pid not in pid_to_team:
            if label in ("home","Home","H","h",1,"1"):
                pid_to_team[pid] = "A"
            elif label in ("away","Away","A","a",0,"0"):
                pid_to_team[pid] = "B"

    all_pids = sorted(set(list(distances.keys()) + list(sprint_seconds.keys())))
    if not any(v == "A" for v in pid_to_team.values()) or not any(v == "B" for v in pid_to_team.values()):
        half = len(all_pids) // 2
        for i, pid in enumerate(all_pids):
            pid_to_team[pid] = "A" if i < half else "B"

    team_metrics = {
        "A": {"name": home_name, "distances": {}, "sprints_seconds": {}, "ids": []},
        "B": {"name": away_name, "distances": {}, "sprints_seconds": {}, "ids": []}
    }

    for pid in all_pids:
        team = pid_to_team.get(pid, "A")
        team_metrics[team]["distances"][pid] = distances.get(pid, 0.0) / 1000.0
        team_metrics[team]["sprints_seconds"][pid] = sprint_seconds.get(pid, 0.0)
        team_metrics[team]["ids"].append(pid)

    for team in ("A","B"):
        tname = team_metrics[team]["name"]
        out_dir = OUTPUT / f"team_{team}_{tname}"
        out_dir.mkdir(parents=True, exist_ok=True)

        def plot(values_map, title, ylabel, filename, color):
            plt.figure(figsize=(12,5))
            items = sorted(values_map.items(), key=lambda kv: kv[1], reverse=True)
            ids = [kv[0] for kv in items]
            vals = [kv[1] for kv in items]
            labels = [id_to_name.get(pid, str(pid)) for pid in ids]
            plt.bar(range(len(vals)), vals, color=color)
            plt.xticks(range(len(vals)), labels, rotation=45, ha="right")
            plt.title(title); plt.ylabel(ylabel)
            plt.tight_layout(); plt.savefig(out_dir / filename, dpi=150); plt.close()

        plot(team_metrics[team]["distances"], f"Distance (km) — {tname}", "Distance (km)",
             f"player_total_distance_{tname}.png", "#FF9999")
        plot(team_metrics[team]["sprints_seconds"], f"Sprint Time (s) — {tname}", "Sprint Seconds",
             f"player_sprint_seconds_{tname}.png", "#9FC5FF")

        fatigue_map = {pid: (team_metrics[team]["distances"][pid] + team_metrics[team]["sprints_seconds"][pid] * 0.02)
                       for pid in team_metrics[team]["ids"]}
        plot(fatigue_map, f"Fatigue Score — {tname}", "Score",
             f"player_fatigue_{tname}.png", "#FFD39F")

        summary = {
            "team_name": tname,
            "num_players_analyzed": len(team_metrics[team]["ids"]),
            "distances_km": {str(pid): team_metrics[team]["distances"][pid] for pid in team_metrics[team]["ids"]},
            "sprint_seconds": {str(pid): team_metrics[team]["sprints_seconds"][pid] for pid in team_metrics[team]["ids"]},
            "fatigue_score": {str(pid): fatigue_map[pid] for pid in fatigue_map},
            "id_to_name": {str(pid): id_to_name.get(pid, None) for pid in team_metrics[team]["ids"]}
        }
        with open(out_dir / f"summary_{tname}.json", "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)

    combined = {"fps_used": fps_use, "teams": {
        "A": {"name": home_name, "num_players": len(team_metrics["A"]["ids"])},
        "B": {"name": away_name, "num_players": len(team_metrics["B"]["ids"])}
    }}
    with open(OUTPUT / "combined_summary.json", "w", encoding="utf-8") as fh:
        json.dump(combined, fh, indent=2)

    print("Model2 team-split complete. Outputs are in:", OUTPUT.resolve())


if __name__ == "__main__":
    run(n_minutes=None)
