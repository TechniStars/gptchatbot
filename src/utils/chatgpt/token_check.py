import os

import tiktoken

from src.config.config import CONFIG


def token_check(text):
    return get_token_count(text) < CONFIG['global_config']['GPT_model']['upper_token_limit_docs']


def limit_text_to_token_limit(text):
    while get_token_count(text) > CONFIG['global_config']['GPT_model']['upper_token_limit_docs']:
        text = text[:-int(len(text)*0.1)]
    return text


def get_token_count(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    token_count = len(encoding.encode(text))
    return token_count


def get_text_from_files(files: list):
    text = ""
    for _, file_path in enumerate(files, start=1):
        with open(file_path, 'r', encoding='utf8') as file:
            filename = os.path.basename(file_path)
            text += f"<#Filename>{filename}</Filename>\n"
            text += f"<#File text summary>Whole file was loaded as Paragraph, no need to summarize file.</File text summary>\n"
            text += f"<#Paragraph>{file.read()}</Paragraph>\n"
    return text
