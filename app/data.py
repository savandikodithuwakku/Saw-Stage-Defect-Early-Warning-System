"""Load exported training artifacts and the small narrative datasets."""

from pathlib import Path
import json
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


def load_json(name: str):
    with (ARTIFACTS / name).open(encoding="utf-8") as file:
        return json.load(file)


def load_products() -> pd.DataFrame:
    return pd.read_csv(ARTIFACTS / "benchmark_products.csv", dtype={"product_id": str})


def load_metrics() -> dict:
    return load_json("metrics.json")
