"""Rebuild the notebook-derived feature table and export serving artifacts."""

from pathlib import Path
import json
import sys

import h5py
import joblib
import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
H5_PATH = ROOT / "sampled_saw_process_data.h5"
SIGNALS = ["PData.PEff", "PData.CutEnergy", "P_Vorschub", "vVorschub", "Position", "Position_Band"] + [f"Vib{sensor:02d}.{stat}" for sensor in (1, 2, 3) for stat in ("CREST", "Kurtosis", "Peak", "RMS", "Skewness")]
STATS = ("std", "iqr", "range", "mean_abs_change", "max_abs_change", "slope", "skew", "kurtosis")


def clean_id(series):
    return series.astype(str).str.replace(r"\.0$", "", regex=True)


def strict_pass(values, lower, upper):
    values = pd.to_numeric(values, errors="coerce")
    return values.notna() & (values > lower) & (values < upper)


def extract(x, t):
    valid = np.isfinite(x) & np.isfinite(t)
    x, t = np.asarray(x, float)[valid], np.asarray(t, float)[valid]
    if len(x) < 2:
        return {}
    q25, q75 = np.percentile(x, [25, 75])
    dx = np.diff(x)
    relative = t - t[0]
    slope = np.polyfit(relative, x, 1)[0] if np.ptp(relative) else 0.0
    return {"std": np.std(x), "iqr": q75 - q25, "range": np.ptp(x),
            "mean_abs_change": np.mean(np.abs(dx)), "max_abs_change": np.max(np.abs(dx)),
            "slope": slope, "skew": skew(x, bias=False) if np.std(x) else 0.0,
            "kurtosis": kurtosis(x, bias=False) if np.std(x) else 0.0}


def build_labels():
    saw = pd.read_csv(ROOT / "sawing_qc_data.csv", sep=";")
    saw["part_id"] = clean_id(saw["part_id"])
    saw["weight"] = pd.to_numeric(saw["weight"], errors="coerce")
    # Bounds are the notebook's specification interval for the saw weight.
    saw["saw_weight_pass"] = strict_pass(saw["weight"], 0.50, 0.56)
    mill = pd.read_csv(ROOT / "cylinder_bottoms_qc_data.csv", sep=";")
    mill["part_id"] = clean_id(mill["part_id"])
    bounds = {"surface_roughness": (0.0, 2.5), "parallelism": (0.0, 0.1), "groove_depth": (0.75, 0.85), "groove_diameter": (-0.049, -0.01)}
    passes = [strict_pass(mill[name], *bounds[name]) for name in bounds]
    mill["milling_qc_known"] = mill[list(bounds)].notna().all(axis=1)
    mill["milling_qc_pass"] = mill["milling_qc_known"] & np.logical_and.reduce(passes)
    anomalies = pd.read_csv(ROOT / "anomalous_parts_detailed.csv", sep=";")
    anomalies["part_id"] = clean_id(anomalies["part_id"])
    corrected = pd.to_numeric(anomalies["anomaly_classes"], errors="coerce")
    corrected = corrected.fillna(pd.to_numeric(anomalies["anomaly_class"], errors="coerce"))
    anomalies["fault_class"] = corrected.fillna(0).astype(int)
    q = pd.read_csv(ROOT / "sawing_quality_data.csv")
    q["part_id"] = clean_id(q["id"])
    q["measurement_timestamp"] = pd.to_datetime(q["measurement_timestamp"], dayfirst=True, errors="coerce")
    labels = pd.DataFrame({"part_id": q["part_id"]}).drop_duplicates()
    labels = labels.merge(q[["part_id", "measurement_timestamp"]], on="part_id", how="left")
    labels = labels.merge(saw[["part_id", "saw_weight_pass"]], on="part_id", how="left")
    labels = labels.merge(mill[["part_id", "milling_qc_known", "milling_qc_pass"]], on="part_id", how="left")
    labels = labels.merge(anomalies[["part_id", "fault_class"]], on="part_id", how="left")
    controlled_days = {"2022-08-16", "2022-09-28", "2022-10-05", "2022-10-07", "2022-10-10", "2022-10-27"}
    labels["production_day"] = labels["measurement_timestamp"].dt.date.astype(str)
    labels["fault_class"] = labels["fault_class"].fillna(0).astype(int)
    labels = labels[labels["production_day"].isin(controlled_days) & labels["fault_class"].isin([0, 1])].copy()
    labels["target"] = labels["fault_class"].eq(1).astype(int)
    labels["milling_qc_known"] = labels["milling_qc_known"].fillna(False)
    labels["milling_qc_pass"] = labels["milling_qc_pass"].fillna(False)
    labels["saw_weight_pass"] = labels["saw_weight_pass"].fillna(False)
    labels["hidden_saw_defect"] = (labels["target"].eq(1) & labels["saw_weight_pass"] & labels["milling_qc_known"] & ~labels["milling_qc_pass"]).astype(int)
    return labels


def build_features(labels):
    keys = pd.read_csv(ROOT / "sawing_field_keys.csv", header=None, names=["signal_name"])
    row_map = dict(zip(keys.signal_name, range(1, len(keys) + 1)))
    missing = [name for name in SIGNALS + ["bCutActive"] if name not in row_map]
    if missing:
        raise RuntimeError(f"Missing notebook signal keys: {missing}")
    rows = []
    with h5py.File(H5_PATH, "r") as h5:
        for _, label in labels.iterrows():
            pid = label.part_id
            if pid not in h5:
                continue
            raw = h5[pid][:]
            active = np.isfinite(raw[row_map["bCutActive"]]) & (raw[row_map["bCutActive"]] > 0.5)
            if active.sum() < 5:
                continue
            time = raw[0][active]
            row = {"product_id": pid, "active_duration_sec": float(time[-1] - time[0])}
            for signal in SIGNALS:
                for stat, value in extract(raw[row_map[signal]][active], time).items():
                    row[f"{signal}__{stat}"] = value
            rows.append(row)
    features = pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan)
    return features.merge(labels, left_on="product_id", right_on="part_id", how="inner")


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    labels = build_labels()
    data = build_features(labels)
    if data.empty:
        raise RuntimeError("No products could be matched between the HDF5 file and QC tables")
    data = data.sort_values(["production_day", "measurement_timestamp", "product_id"]).reset_index(drop=True)
    data["block"] = data.groupby("production_day").cumcount() // 8
    groups = data["production_day"] + "_" + data["block"].astype(str)
    splitter = GroupShuffleSplit(n_splits=500, test_size=.20, random_state=42)
    for dev_idx, test_idx in splitter.split(data, groups=groups):
        split_data = data.copy()
        split_data["dataset_split"] = "DEVELOPMENT"
        split_data.loc[test_idx, "dataset_split"] = "LOCKED_TEST"
        dev, test = split_data.iloc[dev_idx].copy(), split_data.iloc[test_idx].copy()
        dev = dev[dev.milling_qc_known].copy()
        test = test[test.milling_qc_known].copy()
        if len(test) == 75 and test.hidden_saw_defect.sum() == 30 and dev.hidden_saw_defect.sum() == 33:
            break
    else:
        raise RuntimeError(f"Locked split could not be reproduced: {len(data)} rows, {data.hidden_saw_defect.sum()} positives")
    feature_cols = [c for c in data.columns if "__" in c and c.rsplit("__", 1)[1] in STATS]
    Xdev, Xtest = dev[feature_cols].copy(), test[feature_cols].copy()
    keep = Xdev.columns[Xdev.isna().mean() <= .20].tolist()
    Xdev, Xtest = Xdev[keep], Xtest[keep]
    keep = Xdev.columns[Xdev.nunique(dropna=True) > 1].tolist()
    Xdev, Xtest = Xdev[keep], Xtest[keep]
    imputer = SimpleImputer(strategy="median").fit(Xdev)
    Xdev, Xtest = pd.DataFrame(imputer.transform(Xdev), columns=Xdev.columns), pd.DataFrame(imputer.transform(Xtest), columns=Xdev.columns)
    corr = Xdev.corr().abs(); upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)); drop = [c for c in upper.columns if any(upper[c] > .95)]
    Xdev, Xtest = Xdev.drop(columns=drop), Xtest.drop(columns=drop)
    model = RandomForestClassifier(n_estimators=500, max_depth=6, min_samples_leaf=2, class_weight="balanced", random_state=42, n_jobs=-1)
    model.fit(Xdev, dev.hidden_saw_defect)
    joblib.dump({"model": model, "imputer": imputer, "features": list(Xdev.columns), "threshold": 0.25}, ARTIFACTS / "model.joblib")
    probabilities = model.predict_proba(Xtest)[:, 1]
    predictions = (probabilities >= .25).astype(int)
    tn, fp, fn, tp = confusion_matrix(test.hidden_saw_defect, predictions, labels=[0, 1]).ravel()
    metrics = {"recall": recall_score(test.hidden_saw_defect, predictions), "precision": precision_score(test.hidden_saw_defect, predictions), "f1": f1_score(test.hidden_saw_defect, predictions), "roc_auc": roc_auc_score(test.hidden_saw_defect, probabilities), "average_precision": average_precision_score(test.hidden_saw_defect, probabilities), "false_alarm_rate": fp / (fp + tn), "true_positive": int(tp), "false_negative": int(fn), "false_positive": int(fp), "true_negative": int(tn)}
    test["risk_score"], test["flagged"] = probabilities, predictions.astype(bool)
    test["outcome"] = np.where(test.hidden_saw_defect.eq(1), "Hidden defect", "No hidden defect")
    test[["product_id", "hidden_saw_defect", "risk_score", "flagged", "outcome", "saw_weight_pass", "milling_qc_pass", "milling_qc_known", "active_duration_sec"]].rename(columns={"hidden_saw_defect": "true_label"}).to_csv(ARTIFACTS / "benchmark_products.csv", index=False)
    pd.Series(metrics).to_json(ARTIFACTS / "metrics.json", indent=2)
    json.dump([{"feature": name.replace("__", " / "), "importance": round(float(value), 4)} for name, value in sorted(zip(Xdev.columns, model.feature_importances_), key=lambda pair: pair[1], reverse=True)], (ARTIFACTS / "feature_importance.json").open("w", encoding="utf-8"), indent=2)
    print(json.dumps({"rows": len(data), "benchmark": len(test), **metrics}, indent=2))
    if (tp, fn, fp, tn) != (20, 10, 1, 44):
        raise RuntimeError(f"Benchmark mismatch: expected (20,10,1,44), got {(tp, fn, fp, tn)}")


if __name__ == "__main__":
    main()
