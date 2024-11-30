from typing import Generator
from typing_extensions import override
from openai import AssistantEventHandler
import os
from dotenv import load_dotenv
from openai import OpenAI  # Assuming OpenAI is your imported client

# Load the .env file
load_dotenv()

# Get the API key from the environment variable
key = os.getenv("key")

# Initialize the OpenAI client
client = OpenAI(api_key=key)
assistant = client.beta.assistants.create(
  name="Math Tutor",
  instructions="You are a personal math tutor. Write and run code to answer math questions.",
  tools=[{"type": "code_interpreter"}],
  model="gpt-4o",
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)


class StreamHandler(AssistantEventHandler):
    """
    Custom event handler to handle the OpenAI API's response stream.
    """

    def __init__(self):
        self.current_chunk = None
        self.done = False

    @override
    def on_text_created(self, text) -> None:
        """
        Handles the creation of text chunks.
        """
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        """
        Handles incremental updates to the text response.
        """
        self.current_chunk = delta.value
        print(self.current_chunk, end="", flush=True)

    @override
    def on_done(self):
        """
        Indicates that the stream is complete.
        """
        self.done = True


def chat_with_gpt4o_streaming(prompt, client):
    """
    Interact with GPT-4o using a prompt and yield the response in streaming mode.

    Args:
        prompt (str): The user's input prompt.
        client: The OpenAI API client.

    Yields:
        str: Parts of the assistant's response as they arrive.
    """
    handler = StreamHandler()

    # Initialize conversation instructions
    instructions = "You are a helpful assistant."

    try:
        # Use the client to stream responses with the handler
        with client.beta.threads.runs.stream(
            thread_id=thread.id,  # Replace with actual thread ID
            assistant_id=assistant.id,  # Replace with actual assistant ID
            instructions=instructions,
            event_handler=handler,
        ):
            # Continuously yield chunks as they are updated
            while not handler.done:
                if handler.current_chunk is not None:
                    yield handler.current_chunk
                    handler.current_chunk = None  # Reset after yielding
    except Exception as e:
        yield f"Error: {e}"

for response_part in chat_with_gpt4o_streaming("Hello, how are you?", client):
    print(response_part, end="")
