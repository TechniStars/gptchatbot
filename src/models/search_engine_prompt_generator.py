import openai

from src.config.config import CONFIG

openai.api_key = CONFIG['chatgpt_config']['api_key']


class SearchEnginePromptGenerator:
    example1 = "<conversation>" \
               "$Customer$: What is an AI search engine?" \
               "$Assistant$: An AI Search Engine is a powerful tool that can assist with (...)" \
               "$Customer$: Alright, is it a free feature?" \
               "</conversation>" \
               "<keyphrase>AI search engine pricing</keyphrase>"

    example2 = "<conversation>" \
               "$Customer$: How do I configure push notifications?" \
               "$Assistant$: Which notifications are you referring to, web or mobile?" \
               "$Customer$: I mean the web ones." \
               "</conversation>" \
               "<keyphrase>Configuring web push notifications</keyphrase>"

    example3 = "<conversation>" \
               "$Customer$: How can I create an account?" \
               "$Assistant$: Are you looking to create a personal account or one for your company?" \
               "$Customer$: It's just for my experimental purposes." \
               "</conversation>" \
               "<keyphrase>Creating a personal account</keyphrase>"

    prompt = f"Your job is to extract the keyphrase for the last Customer intent from the given conversation included in triple backticks. " \
             f"The conversation is between Q&A Assistant, marked as &Assistant&, and Customer, marked as &Customer&. " \
             f"First, extract the last Customer intent. Ignore previous Customer intents and treat previous messages only as context. " \
             f"The last Customer message have the biggest impact on keyphrase. Give it much higher weight than previous messages." \
             f"Next, construct a keyphrase that can help the vector search engine find an answer for the last Customer intent. " \
             f"Do not extract intent from Assistant messages." \
             f"The keyphrase must be in plain text and should be understandable by the vector search engine. " \
             f"Return only the keyphrase that can be used for the vector search engine." \
             f"Always but always use only english language when formulating keyphrases, " \
             f"you will have to translate other languages if customer doesn't speak english." \
             f"Do it by analogy of these examples, where conversation is closed in <conversation> tag and keyphrase relevant to it in <keyphrase>:" \
             f"<example>{example1}</example>\n" \
             f"<example>{example2}</example>\n" \
             f"<example>{example3}</example>\n"

    @staticmethod
    def generate_search_engine_prompt(chat_history, temperature=0):
        conversation_string = SearchEnginePromptGenerator.generate_conversation_string(chat_history)
        messages = [{'role': 'user', 'content': f'{SearchEnginePromptGenerator.prompt}\n```{conversation_string}```'}]

        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temperature
        )

        response = chat.choices[0].message.content.lower()
        response = response.replace('keyphrase:', '').strip()

        return response

    @staticmethod
    def generate_conversation_string(chat_messages):
        result = ""
        for message in chat_messages:
            if message['role'] == 'user':
                result += f"$Customer$: {message['content']}\n"
            elif message['role'] == 'assistant':
                result += f"$Assistant$: {message['content']}\n"
        return result
