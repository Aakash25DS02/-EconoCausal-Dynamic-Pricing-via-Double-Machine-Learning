
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

from discount_optimizer import recommend_discount

app = FastAPI(
    title="EconoCausal API",
    description="Backend for discount analysis and pricing recommendations.",
    version="0.2.0",
)

PROJECT_DIR = Path(__file__).resolve().parent

DATA_CANDIDATES = [
    PROJECT_DIR / "data" / "pricing_data.csv",
    PROJECT_DIR / "pricing_data.csv",
    PROJECT_DIR.parent / "data" / "pricing_data.csv",
    PROJECT_DIR.parent / "backend" / "data" / "pricing_data.csv",
    PROJECT_DIR.parent.parent / "data" / "pricing_data.csv",
    PROJECT_DIR.parent.parent / "backend" / "data" / "pricing_data.csv",
]

DATA_PATH = next(
    (path for path in DATA_CANDIDATES if path.exists()),
    PROJECT_DIR.parent / "data" / "pricing_data.csv",
)

REQUIRED_COLUMNS = ["price", "discount", "purchase"]


def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Dataset not found. Ensure pricing_data.csv "
                "exists in the project data folder."
            ),
        )

    try:
        df = pd.read_csv(DATA_PATH)
    except (OSError, pd.errors.ParserError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read the pricing dataset: {exc}",
        ) from exc

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {missing_columns}",
        )

    if df.empty:
        raise HTTPException(
            status_code=422,
            detail="The pricing dataset contains no records.",
        )

    if df[REQUIRED_COLUMNS].isnull().any().any():
        raise HTTPException(
            status_code=422,
            detail="Required columns contain missing values.",
        )

    return df


@app.get("/")
def root():
    return {
        "project": "EconoCausal",
        "message": "Dynamic pricing and causal analysis API",
        "version": "0.2.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/data/summary")
def data_summary():
    df = load_dataset()

    return {
        "dataset_path": str(DATA_PATH),
        "rows": len(df),
        "columns": list(df.columns),
        "missing_values": {
            column: int(count)
            for column, count in df.isnull().sum().items()
        },
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
    return {
        "records": df.head(10).to_dict(orient="records")
    }


@app.get("/discount/recommendation")
def discount_recommendation():
    try:
        return recommend_discount()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
