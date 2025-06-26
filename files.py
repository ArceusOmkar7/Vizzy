import pandas as pd
from pathlib import Path


def load_csv_to_df(path: str) -> pd.DataFrame | None:
    if not path:
        print("Path not entered")
        return None

    p = Path(path)

    if not p.exists():
        print(f"File does not exist: {p}")
        return None
    try:
        df = pd.read_csv(p)
        # print("File Loaded")
        return df
    except pd.errors.EmptyDataError:
        print("File is empty.")
        return None
    except pd.errors.ParserError as e:
        print(f"Parsing error: {e}")
        return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None
