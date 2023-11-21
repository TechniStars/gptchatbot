function_descriptions = [
    {
        "name": "respond_to_client",
        "description": "Generate a response as the chatbot to the user's query by providing detailed and accurate information based on the provided documentation or products.",
        "parameters": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "The generated response of the AI product assistant to the user's query. This response should be comprehensive, accurate, and directly address the user's question or request. Ensure that the response is detailed enough to assist the user effectively. The response must not be empty.",
                }
            },
            "required": ["response"],
        },
    }
]
