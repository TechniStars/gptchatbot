import os
import pickle
import re
from pathlib import Path

import telegram
from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from src.chatgpt.chatbot import Chatbot
from src.config.config import CONFIG
from src.models.model_aggregator import ModelAggregator
from src.models.search_engine_prompt_generator import SearchEnginePromptGenerator
from src.utils.singleton import singleton


@singleton
class TelegramBot:
    def __init__(self):
        self.TOKEN = CONFIG['telegram_config']['token']
        self.BOT_USERNAME = '@' + CONFIG['telegram_config']['bot_username']
        self.WHITELIST = CONFIG['telegram_config']['whitelist']
        self.bot = telegram.Bot(token=self.TOKEN)
        self.message_history_dir = 'message_history'
        self.chatbot_GPT = Chatbot()
        self.search_engine = ModelAggregator()
        self.search_engine_prompt_generator = SearchEnginePromptGenerator()
        os.makedirs(self.message_history_dir, exist_ok=True)

    # Responses
    async def handle_response(self, user_question: str, chat_id: int, message_history) -> str:
        question_keywords = self.search_engine_prompt_generator.generate_search_engine_prompt(
            message_history + [{'role': 'user', 'content': user_question}])

        # Load message history
        self.chatbot_GPT.clear_conversation()
        if message_history:
            self.chatbot_GPT.messages = message_history

        # Search for relevant files/paragraphs in documentation
        source_text = self.search_engine.get_source_text(question_keywords)
        if CONFIG['telegram_config']['send_source_text_as_file']:
            await self.__send_source_text_as_file(source_text, question_keywords, chat_id)

        # Update system prompt in GPT model to contain new documentation
        self.chatbot_GPT.set_documentation_and_system_prompt(source_text)

        answer_from_chat = self.chatbot_GPT.generate_chatbot_reply(user_question)
        return answer_from_chat

    async def __send_source_text_as_file(self, source_text, question_keywords, chat_id):
        if source_text is not None and len(source_text) > 0:
            # Create a temporary file and write the paragraphs into it
            cleaned_text = re.sub(r'[^a-zA-Z\s]', '', question_keywords)
            word_list = [word for word in cleaned_text.split() if word.isalpha()]
            filename = f'{"_".join(word_list)[:50]}.txt'

            if not filename:
                filename = 'context.txt'
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(source_text)

            # Send the file to the desired Telegram chat
            with open(filename, 'rb') as file:
                await self.bot.send_document(chat_id=chat_id, document=InputFile(file))

            # Delete the temporary file
            os.remove(filename)

    def verify_user(self, message_type, chat_id):
        if not CONFIG['telegram_config']['allow_only_whitelist']:
            return True

        if 'group' in message_type:
            return str(chat_id) in self.WHITELIST['groups']
        else:
            return str(chat_id) in self.WHITELIST['users']

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_type = update.message.chat.type
        chat_id = update.message.chat.id
        if not self.verify_user(message_type, chat_id):
            print(f"User {chat_id} - verification failed.")
            await update.message.reply_text("You are not allowed to chat.")
            return

        message_history = []
        try:
            message_id_from_user = update.message.reply_to_message.message_id
            old_history_filepath = str(Path(self.message_history_dir, str(message_id_from_user) + '.pkl'))
            with open(old_history_filepath, 'rb') as f:
                message_history = pickle.load(f)
        except Exception:
            pass

        # Get message text and remove annotation if necessary
        user_message_text = update.message.text
        if message_type == 'group' and (self.BOT_USERNAME in user_message_text or message_history):
            user_message_text = user_message_text.replace(self.BOT_USERNAME, "").strip()
        elif message_type == 'private':
            pass
        else:
            return

        print(f'User ({chat_id}) in {message_type}: "{user_message_text}"')

        response = await self.handle_response(user_message_text, chat_id, message_history)
        message_sent = await update.message.reply_text(response)

        # Save current message chain
        new_history_filepath = str(Path(self.message_history_dir, str(message_sent.message_id) + '.pkl'))
        with open(new_history_filepath, 'wb') as f:
            pickle.dump(self.chatbot_GPT.messages, f)

    def run(self):
        print('Bot is running.')
        app = Application.builder().token(self.TOKEN).build()

        # Message handlers
        app.add_handler(MessageHandler(filters.TEXT, self.handle_message))

        # Run
        app.run_polling(poll_interval=1)


def launch_telegram():
    bot = TelegramBot()
    bot.run()
