"""Adaptador inbound HTTP (FastAPI) del servicio ML."""

from fastapi import FastAPI
from pydantic import BaseModel

from composition import estimate_use_case

app = FastAPI(title="WEB_MINERA ML", version="1.0.0")


class EstimateRequest(BaseModel):
    origin_quantity: float
    mineral: str | None = None
    unit: str | None = None
    observed_quantity: float | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/inference/estimate")
def estimate(payload: EstimateRequest) -> dict:
    use_case = estimate_use_case()
    return use_case.execute(payload.model_dump())
