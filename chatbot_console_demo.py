import pickle
import re

from src.models.model_aggregator import ModelAggregator
from src.models.search_engine_prompt_generator import SearchEnginePromptGenerator
from src.chatgpt.chatbot import Chatbot

chatbot_GPT = Chatbot()

while True:
    # Load msg history
    message_history = []
    history_filepath = 'message_history.pkl'
    try:
        with open(history_filepath, 'rb') as f:
            message_history = pickle.load(f)
            for line in message_history:
                print(line)
    except Exception:
        pass

    text = input('User: ')

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
        filename = f'{"_".join(word_list)[:50]}.txt'

        if not filename:
            filename = 'context.txt'
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(source_text)

        # Delete the temporary file
        # os.remove(filename)

    print(f"Answer:\n{answer_from_chat}\n")

    # Save current message chain
    with open(history_filepath, 'wb') as f:
        pickle.dump(chatbot_GPT.messages, f)
