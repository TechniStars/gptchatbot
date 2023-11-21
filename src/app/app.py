import os

from src.config.config import CONFIG
from src.utils.solution_utils import get_project_root

os.chdir(get_project_root())
import uuid
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
import pickle
import re

from src.models.model_aggregator import ModelAggregator
from src.models.search_engine_prompt_generator import SearchEnginePromptGenerator
from src.chatgpt.chatbot import Chatbot

app = FastAPI()
chatbot_GPT = Chatbot()
os.makedirs(str(Path(get_project_root(), 'data', 'api_files')), exist_ok=True)


@app.get("/conversation/")
async def conversation(text: str, conversation_id: str = None):
    if conversation_id:
        # Load msg history
        history_filepath = str(Path(get_project_root(), 'data', 'api_files', str(conversation_id)+'.pkl'))
        history_filepath.split()
        try:
            with open(history_filepath, 'rb') as f:
                message_history = pickle.load(f)
        except Exception:
            raise HTTPException(status_code=422, detail=str('No conversation with this id found'))
    else:
        conversation_id = uuid.uuid4()
        message_history = []
        history_filepath = str(Path(get_project_root(), 'data', 'api_files', str(conversation_id)+'.pkl'))
        history_filepath.split()
    model_keyword = SearchEnginePromptGenerator()
    question_keywords = model_keyword.generate_search_engine_prompt(
        message_history + [{'role': 'user', 'content': text}])

    # Load message history
    chatbot_GPT.clear_conversation()

    print(f'Keywords for search: {question_keywords}')

    model = ModelAggregator()
    source_text = model.get_source_text(question_keywords)

    # If no history or docs needs to be updated -> update
    if message_history:
        chatbot_GPT.messages = message_history

    chatbot_GPT.set_documentation_and_system_prompt(source_text)

    answer_from_chat = chatbot_GPT.generate_chatbot_reply(text)

    if source_text:
        # Create a temporary file and write the paragraphs into it
        cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
        word_list = [word for word in cleaned_text.split() if word.isalpha()]
        # filename = f'{"_".join(word_list)[:50]}.txt'
        filename = f'{conversation_id}.txt'
        if not filename:
            filename = 'context.txt'

        save_file = Path(get_project_root(), 'data', 'api_files', filename)

        with open(save_file, 'w', encoding='utf-8') as file:
            file.write(source_text)

    print(f"Answer:\n{answer_from_chat}\n")
    print(f"conversation id {conversation_id} ")

    # Save current message chain
    with open(history_filepath, 'wb') as f:
        pickle.dump(chatbot_GPT.messages, f)
    return {"message": answer_from_chat, 'conversation_id': conversation_id}


@app.get("/conversation_history/")
async def conversation(conversation_id: str = None):
    if conversation_id:
        # Load msg history
        history_filepath = str(Path(get_project_root(), 'data','api_files',str(conversation_id)+'.pkl'))
        history_filepath.split()
        try:
            with open(history_filepath, 'rb') as f:
                message_history = pickle.load(f)
                return message_history[1:]
        except Exception:
            raise HTTPException(status_code=422, detail=str('No conversation with this id found'))

    raise HTTPException(status_code=422, detail=str('Missing conversation id'))


def launch_api():
    host = CONFIG['api_config']['host']
    port = CONFIG['api_config']['port']
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    launch_api()
