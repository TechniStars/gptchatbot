import glob
import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from src.chatgpt.gpt_tasks_utils import read_source_file, generate_chat_response, convert_json_str_to_dicts
from src.utils.solution_utils import get_project_root


def system_prompt(n_questions_per_doc=10):
    prompt = """Your job is to read given text and create""" + str(n_questions_per_doc) + """Q&A pairs basing on this. 
    Each question and answer must be included in text. 
    Return it as JSON list like:
    [{"question": "How can i ..?", "answer": "some answer"}, {"question": "question2", "answer": "answer 2..."}, ...]"""
    return prompt


def generate_qa(file_path):
    content = read_source_file(file_path)
    file_name = os.path.basename(file_path)

    functions = [{"name": "get_qa", "parameters": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Example question user can ask about the "
                                                                      "provided text."},
                        "answer": {"type": "string", "description": "Answer for the user's question."}
                    }
                }
            }
        },
        "required": ["questions"],
    }}]

    chat_response = generate_chat_response(content, system_prompt(), functions)
    qa_list = convert_json_str_to_dicts(chat_response)
    qa_list = qa_list['questions']

    for i in range(len(qa_list)):
        qa_list[i]['source'] = file_name

    return qa_list


def main():
    data_path = str(Path(get_project_root(), 'data', 'raw'))
    csv_path = str(Path(get_project_root(), 'data', 'questions', 'valid_questions.csv'))
    print(f'Generating Q&A from {data_path}, saving to {csv_path}...')

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame({'question': [], 'answer': [], 'source': []})

    remaining_files = glob.glob(str(Path(data_path, '*.*')))
    remaining_files = [fp for fp in remaining_files if os.path.basename(fp) not in df['source'].values]

    for i, file_path in tqdm(enumerate(remaining_files), desc="QA generation", total=len(remaining_files)):
        try:
            print(f'Generating summaries - {i} / {len(remaining_files)}')
            # Generate Q&A
            qa = generate_qa(file_path)
            df = pd.concat([df, pd.DataFrame(qa)], ignore_index=True)

            # Update csv
            df.to_csv(csv_path, index=False)
        except Exception as e:
            print(f'Skipping {file_path} due to an exception: {e}')
