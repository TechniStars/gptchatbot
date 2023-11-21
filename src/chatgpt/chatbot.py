import openai

from src.chatgpt.functions_openai import function_descriptions
from src.chatgpt.system_prompt import generate_system_prompt
from src.config.config import CONFIG
from src.utils.chatgpt.token_check import get_token_count
from src.utils.url_utils import check_multiple_urls_in_text

openai.api_key = CONFIG['chatgpt_config']['api_key']


class Chatbot:
    def __init__(self, messages=None, temperature=0.0):
        if messages:
            self.messages = messages
        else:
            self.messages = []
        self.temperature = temperature

    def set_documentation_and_system_prompt(self, documentation):
        """
        documentation: str
            The source text in which to look for the answer to the question.
        """
        system_prompt = {'role': 'system', 'content': generate_system_prompt(documentation)}
        if self.messages:
            self.messages[0] = system_prompt
        else:
            self.messages.append(system_prompt)

    def _prepare_messages_to_chat(self):
        messages_to_chat = []
        for message in self.messages:
            if message.get('content'):
                messages_to_chat.append(message)
            else:
                messages_to_chat.append({'role': message['role'],
                                         'content': message['function_call']['arguments']['response']})
        return messages_to_chat

    def generate_chatbot_reply(self, question):
        """
        Generates a chatbot reply to a user's question.

        Parameters
        ----------
        question : str
            The user's question or input.

        Returns
        -------
        str
            The chatbot's response to the user's input.
        """

        user_prompt = {'role': 'user', 'content': question}
        self.messages.append(user_prompt)

        messages_to_chat = self._prepare_messages_to_chat()
        tokens_used = get_token_count(str(messages_to_chat) + str(function_descriptions))

        if tokens_used < 4096:
            model_name = "gpt-3.5-turbo"
        else:
            model_name = "gpt-3.5-turbo-16k"
            while get_token_count(str(messages_to_chat) + str(function_descriptions)) > CONFIG['global_config']['GPT_model']['upper_token_limit']:
                self.messages.pop(1)
                messages_to_chat = self._prepare_messages_to_chat()

        chat = openai.ChatCompletion.create(
            model=model_name,
            messages=messages_to_chat,
            temperature=self.temperature
        )

        assistant_response = chat.choices[0]['message']['content']
        self.messages.append({'role': 'assistant', 'content': assistant_response})

        if CONFIG['chatgpt_config']['system_prompt']['prevent_fake_urls_in_response']:
            # Remove invalid URLs
            assistant_response = self._remove_invalid_urls(assistant_response)

        return assistant_response

    def clear_conversation(self):
        """
        Clears history of the conversation with Chatbot.
        """
        self.messages = []

    def _remove_invalid_urls(self, message):
        url_validity = check_multiple_urls_in_text(message)
        if False in url_validity.values():
            invalid_urls = '\n'.join(
                [f'Please remove any mentions about {link}' for link in url_validity if not url_validity[link]])
            messages = [{'role': 'system',
                         'content': "Please review the following message and remove any mentions of URLs that user will ask about. "
                                    "There can't be any urls user asked to remove, also if you remove any urls that weren't mentioned by user in the final message or you fill fail your job and be sent to gulag.\n"
                                    f"Message:\n{message}"}]
            user_prompt = {'role': 'user', 'content': f"Removal request :\n{invalid_urls}"}

            messages.append(user_prompt)

            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=self.temperature
            )

            message = chat.choices[0]['message']['content']
        return message
