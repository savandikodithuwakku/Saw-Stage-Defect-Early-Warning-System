from typing import Any

from pydantic import BaseModel, Field


class Overview(BaseModel):
    misalignments: int
    saw_weight_pass_rate: float
    later_milling_failures: int
    explanation: str


class PipelineStage(BaseModel):
    number: int
    title: str
    description: str
    icon: str


class BenchmarkMetrics(BaseModel):
    recall: float
    precision: float
    f1: float
    roc_auc: float
    average_precision: float
    false_alarm_rate: float
    true_positive: int
    false_negative: int
    false_positive: int
    true_negative: int


class BenchmarkProduct(BaseModel):
    product_id: str
    true_label: int
    risk_score: float
    flagged: bool
    outcome: str


class EarlyWarningPoint(BaseModel):
    checkpoint: str
    seconds: float | None
    caught: int
    total: int


class ProductDetail(BenchmarkProduct):
    top_features: list[dict[str, Any]] = Field(default_factory=list)
