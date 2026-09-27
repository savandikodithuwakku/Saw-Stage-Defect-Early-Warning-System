"""Serving access to the model exported by scripts/train_and_export.py."""

from functools import lru_cache

import h5py
import numpy as np
import pandas as pd

from .data import ROOT
from .data import load_json, load_metrics, load_products


@lru_cache(maxsize=1)
def model_bundle() -> dict:
    return {
        "metrics": load_metrics(),
        "products": load_products(),
        "features": load_json("feature_importance.json"),
    }


def product_detail(product_id: str) -> dict | None:
    bundle = model_bundle()
    rows = bundle["products"]
    match = rows[rows["product_id"].astype(str) == str(product_id)]
    if match.empty:
        return None
    row = match.iloc[0].to_dict()
    row["product_id"] = str(row["product_id"])
    row["true_label"] = int(row["true_label"])
    row["risk_score"] = float(row["risk_score"])
    row["flagged"] = bool(row["flagged"])
    row["top_features"] = bundle["features"][:5]
    return row


def investigation(product_id: str) -> dict | None:
    """Return historical QC context and downsampled active-cut signals."""
    row = product_detail(product_id)
    if row is None:
        return None
    keys = pd.read_csv(ROOT / "sawing_field_keys.csv", header=None, names=["signal_name"])
    row_map = dict(zip(keys.signal_name, range(1, len(keys) + 1)))
    signals = {
        "Power": "PData.PEff",
        "Feed": "vVorschub",
        "Position": "Position",
        "Vibration": "Vib01.RMS",
    }
    with h5py.File(ROOT / "sampled_saw_process_data.h5", "r") as h5:
        if str(product_id) not in h5:
            return None
        raw = h5[str(product_id)][:]
    active = np.isfinite(raw[row_map["bCutActive"]]) & (raw[row_map["bCutActive"]] > 0.5)
    time = raw[0][active]
    result_signals = []
    for label, signal_name in signals.items():
        values = raw[row_map[signal_name]][active]
        finite = np.isfinite(values) & np.isfinite(time)
        points = [{"seconds": round(float(t - time[0]), 3), "value": round(float(v), 5)} for t, v in zip(time[finite], values[finite])]
        if len(points) > 80:
            positions = np.linspace(0, len(points) - 1, 80).astype(int)
            points = [points[index] for index in positions]
        result_signals.append({"name": label, "signal": signal_name, "points": points})
    row["duration_seconds"] = round(float(time[-1] - time[0]), 2) if len(time) else 0
    row["saw_weight_pass"] = bool(row.get("saw_weight_pass", False))
    row["milling_qc_pass"] = bool(row.get("milling_qc_pass", False))
    row["milling_qc_known"] = bool(row.get("milling_qc_known", False))
    row["signals"] = result_signals
    return row
