import os.path
from pathlib import Path

import pandas as pd

from src.utils.solution_utils import get_project_root


def get_summary_from_filepath(file_path: str):
    file_path = os.path.basename(file_path)
    df = pd.read_csv(str(Path(get_project_root(), 'data', 'summaries', 'summaries.csv')))
    matching_row = df.loc[df['filename'] == file_path]

    if not matching_row.empty:
        # If a matching row is found, return the 'summary' value from that row
        return matching_row['summary'].values[0]
    else:
        # If no matching row is found, raise an exception
        raise ValueError(f"No matching summary found for file_path: {file_path}")
