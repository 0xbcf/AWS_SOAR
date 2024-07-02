import openai
import logging

logger = logging.getLogger()
logger.setLevel("INFO")


def get_chat_response(creds, message):
    # Send a chat question to ChatGPT and return the output
    client = openai.OpenAI(api_key=creds.get('key'))
    messages = [{
        "role": "user",
        "content": "{}".format(message)
    }]
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-4o"
    )
    return chat_completion.choices[0].message.content


def get_embedding(creds, data):
    # Used to convert text into machine-understandable vector/embedding
    client = openai.OpenAI(api_key=creds.get('key'))
    response = client.embeddings.create(
        input=data,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding
