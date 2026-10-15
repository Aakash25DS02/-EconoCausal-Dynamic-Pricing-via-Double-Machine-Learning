
from pathlib import Path
import pandas as pd


def get_project_root() -> Path:
    """Return the EconoCausal repository root."""
    return Path(__file__).resolve().parents[2]


def load_dataset(file_path=None) -> pd.DataFrame:
    """Load the raw retail customer dataset."""
    if file_path is None:
        file_path = (
            get_project_root()
            / "member_4_mahesh"
            / "shared"
            / "data"
            / "raw"
            / "retail_customers.csv"
        )


    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}. "
            "Check that the CSV exists in shared/data/raw/."
        )

    return pd.read_csv(file_path)


def save_dataset(df: pd.DataFrame, file_path=None) -> Path:
    """Save a processed dataset as CSV."""
    if file_path is None:
        file_path = (
            get_project_root()
            / "shared"
            / "data"
            / "processed"
            / "retail_customers_clean.csv"
        )

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False)

    return file_path


if __name__ == "__main__":
    # Test loading the dataset directly
    df = load_dataset()
    print("Dataset loaded successfully!")
    print(f"Dataset shape: {df.shape}")
    print(df.head())