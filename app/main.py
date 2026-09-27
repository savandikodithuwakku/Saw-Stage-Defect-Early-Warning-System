"""FastAPI application for the Saw-stage early warning demo."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .data import load_json, load_metrics, load_products
from .model import investigation, product_detail
from .schemas import BenchmarkMetrics, BenchmarkProduct, Overview, PipelineStage, ProductDetail


app = FastAPI(title="Saw-stage Early Warning", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/overview", response_model=Overview)
def overview():
    return load_json("overview.json")


@app.get("/api/pipeline", response_model=list[PipelineStage])
def pipeline():
    return load_json("pipeline.json")


@app.get("/api/benchmark/metrics", response_model=BenchmarkMetrics)
def benchmark_metrics():
    return load_metrics()


@app.get("/api/benchmark/products", response_model=list[BenchmarkProduct])
def benchmark_products():
    return load_products().to_dict(orient="records")


@app.get("/api/model-comparison")
def model_comparison():
    return load_json("model_comparison.json")


@app.get("/api/model-features")
def model_features():
    return load_json("feature_importance.json")[:8]


@app.get("/api/early-warning")
def early_warning():
    return load_json("early_warning.json")


@app.get("/api/business-value")
def business_value():
    return load_json("business_value.json")


@app.get("/api/limitations")
def limitations():
    return load_json("limitations.json")


@app.get("/api/predict/{product_id}", response_model=ProductDetail)
def predict(product_id: str):
    result = product_detail(product_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Benchmark product not found")
    return result


@app.get("/api/investigation/{product_id}")
def product_investigation(product_id: str):
    result = investigation(product_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Benchmark product not found")
    return result
