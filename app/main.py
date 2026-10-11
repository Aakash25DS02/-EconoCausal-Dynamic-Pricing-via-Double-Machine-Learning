
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="EconoCausal API",
    description="Backend for causal discount analysis and budget-aware pricing.",
    version="0.1.0",
)

BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BACKEND_DIR / "data" / "pricing_data.csv"

REQUIRED_COLUMNS = [
    "price",
    "discount",
    "purchase",
]


def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Dataset not found. Run python generate_data.py first.",
        )

    df = pd.read_csv(DATA_PATH)

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {missing_columns}",
        )

    return df


@app.get("/")
def root():
    return {
        "project": "EconoCausal",
        "message": "Dynamic pricing and causal analysis API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/data/summary")
def data_summary():
    df = load_dataset()

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "purchase_rate": round(float(df["purchase"].mean()), 4),
        "average_discount": round(float(df["discount"].mean()), 4),
        "average_price": round(float(df["price"].mean()), 2),
        "discount_range": [
            float(df["discount"].min()),
            float(df["discount"].max()),
        ],
    }


@app.get("/data/preview")
def data_preview():
    df = load_dataset()
    return {"records": df.head(10).to_dict(orient="records")}
