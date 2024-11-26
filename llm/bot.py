import os
from dotenv import load_dotenv
from openai import OpenAI  # Assuming OpenAI is your imported client

# Load the .env file
load_dotenv()

# Get the API key from the environment variable
key = os.getenv("key")

# Initialize the OpenAI client
client = OpenAI(api_key=key)
def chat_with_gpt4o_streaming(prompt):
    """
    Interact with GPT-4o using a prompt and return the response in streaming mode.

    Args:
        prompt (str): The user's input prompt.
        client: The OpenAI API client.

    Returns:
        generator: A generator yielding parts of the GPT-4o response as they arrive.
    """
    # Initialize conversation history with a system role
    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        # Request a response from GPT-4o in streaming mode
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history,
            stream=True
        )

        # Yield each part of the assistant's message as it arrives
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    except Exception as e:
        # Yield the error message if an exception occurs
        yield f"Error: {e}"

# Example usage:
for part in chat_with_gpt4o_streaming("say hello in 3 diff lines"):
    print(part, end="")
