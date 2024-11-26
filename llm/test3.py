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

def stream_response(client, thread_id, assistant_id, prompt):
    """
    Streams a response from the OpenAI Assistant API based on the given prompt.

    Parameters:
        client: The OpenAI client instance.
        thread_id: The thread ID for the session.
        assistant_id: The assistant ID for the session.
        prompt: The prompt string to send to the assistant.

    Yields:
        Streamed response text as it is received.
    """

    class EventHandler(AssistantEventHandler):
        def __init__(self):
            self.text_accumulator = ""

        @override
        def on_text_created(self, text) -> None:
            print(f"\nassistant > ", end="", flush=True)

        @override
        def on_text_delta(self, delta, snapshot):
            self.text_accumulator += delta.value
            print(delta.value, end="", flush=True)

        def get_text(self):
            return self.text_accumulator

    event_handler = EventHandler()

    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please address the user as Jane Doe. The user has a premium account.",
        event_handler=event_handler,
    ) as stream:
        for event in stream:
            if event.event == "thread.message.delta":
                yield event_handler.get_text()



for response in stream_response(client, thread.id, assistant.id, "hi"):
    print(response)
