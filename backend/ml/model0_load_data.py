import json
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent / "data"

TRACKING_FILE = BASE / "1925299_tracking_extrapolated.jsonl"
MATCH_FILE = BASE / "1925299_match.json"
EVENTS_FILE = BASE / "1925299_dynamic_events.csv"
PHASES_FILE = BASE / "1925299_phases_of_play.csv"


def load_tracking():
    print("Loading tracking data JSONL...")

    frames = []
    with open(TRACKING_FILE, "r", encoding="utf-8") as f:

        for line in f:
            line = line.strip()
            if not line:
                continue
            frames.append(json.loads(line))

    print(f"Loaded {len(frames):,} tracking frames.")
    return frames


def load_match_metadata():
    print("Loading match metadata...")
    with open(MATCH_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)
    print("Match metadata loaded.")
    return meta



def load_events():
    print("Loading dynamic events CSV...")
    df_events = pd.read_csv(EVENTS_FILE)
    print(f"Loaded {len(df_events):,} events.")
    return df_events


def load_phases():
    print("Loading phases of play CSV...")
    df_phases = pd.read_csv(PHASES_FILE)
    print(f"Loaded {len(df_phases):,} phases.")
    return df_phases


if __name__ == "__main__":
    tracking = load_tracking()
    meta = load_match_metadata()
    events = load_events()
    phases = load_phases()

    print("\nEverything loaded successfully!")
