from flask import Blueprint, jsonify
from pathlib import Path
from config import Config

from ml.model0_load_data import load_tracking, load_match_metadata
from ml.model1 import run_model1
from ml.model2_real import run_model2
from ml.model3_fixed import run_model3

analysis_bp = Blueprint("analysis_bp", __name__)

OUTPUT_BASE = Path(Config.OUTPUT_DIR)

def ensure_out(subfolder: str) -> Path:
    out_dir = OUTPUT_BASE / subfolder
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

@analysis_bp.post("/tactical-shape")
def tactical_shape():
    frames = load_tracking()
    meta = load_match_metadata()
    out_dir = ensure_out("model1")

    run_model1(frames, meta, out_dir, n_minutes=5)

    files = [f.name for f in out_dir.glob("*.png")]
    urls = [f"/outputs/model1/{name}" for name in files]
    return jsonify({"message": "Model 1 complete", "files": urls}), 200

@analysis_bp.post("/player-performance")
def player_performance():
    frames = load_tracking()
    out_dir = ensure_out("model2")

    run_model2(frames, out_dir, n_minutes=5)

    files = [f.name for f in out_dir.glob("*.png")]
    urls = [f"/outputs/model2/{name}" for name in files]
    return jsonify({"message": "Model 2 complete", "files": urls}), 200

@analysis_bp.post("/pitch-control")
def pitch_control():
    frames = load_tracking()
    meta = load_match_metadata()
    out_dir = ensure_out("model3")

    run_model3(frames, meta, out_dir, n_minutes=5)

    files = [f.name for f in out_dir.glob("*.png")]
    urls = [f"/outputs/model3/{name}" for name in files]
    return jsonify({"message": "Model 3 complete", "files": urls}), 200
