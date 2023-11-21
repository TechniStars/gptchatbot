import glob
import os
from pathlib import Path

import pandas as pd

from src.chatgpt.gpt_tasks_utils import read_source_file, generate_chat_response
from src.utils.solution_utils import get_project_root


def system_prompt():
    prompt = """Your task is to provide a concise summary of the given text. 
    The summary should be limited to a maximum of three sentences and must effectively convey 
    the type of information contained in the text.
    Return summary as plain text."""
    return prompt


def generate_summary(file_path):
    content = read_source_file(file_path)
    file_name = os.path.basename(file_path)

    chat_response = (generate_chat_response(content, system_prompt()))
    return {'filename': file_name, 'summary': chat_response}


def main():
    data_path = str(Path(get_project_root(), 'data', 'raw'))
    csv_path = str(Path(get_project_root(), 'data', 'summaries', 'summaries.csv'))
    print(f'Generating Q&A from {data_path}, saving to {csv_path}...')

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame({'filename': [], 'summary': []})

    remaining_files = glob.glob(str(Path(data_path, '*.*')))
    remaining_files = [fp for fp in remaining_files if os.path.basename(fp) not in df['filename'].values]

    while remaining_files:
        for file_path in remaining_files:
            print(f'Generating summaries - {len(df)} / {len(df) + len(remaining_files)}')
            try:
                # Generate summary
                summary = generate_summary(file_path)
                df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)

                # Update csv
                df.to_csv(csv_path, index=False)

                # Mark file as done
                remaining_files.remove(file_path)
            except Exception as e:
                print(f'Skipping {file_path} due to an exception: {e}')

        if remaining_files:
            print(f'Trying to generate again summaries for {len(remaining_files)} files...')
    print("Succesfully generated summaries for all files.")
