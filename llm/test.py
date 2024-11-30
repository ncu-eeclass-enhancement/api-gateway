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


class EventHandler(AssistantEventHandler):
    """Custom event handler to process streaming responses."""

    def __init__(self):
        self.response_buffer = []

    @override
    def on_text_created(self, text) -> None:
        pass  # No need to explicitly handle text creation

    @override
    def on_text_delta(self, delta, snapshot):
        self.response_buffer.append(delta.value)
        print(delta.value, end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


def stream_prompt_response(client, thread_id: str, assistant_id: str, prompt: str) -> Generator[str, None, None]:
    """
    Stream the response for a given prompt.

    Args:
        client: The OpenAI client instance.
        thread_id: The thread ID.
        assistant_id: The assistant ID.
        prompt: The prompt string to send.

    Yields:
        str: Segments of the response as they are streamed.
    """
    handler = EventHandler()
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt #"I need to solve the equation `3x + 11 = 14`. Can you help me?"
    )
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please address the user as Jane Doe. The user has a premium account.",
        event_handler=handler,
    ) as stream:
        for delta in stream.until_done():
            if handler.response_buffer:
                yield ''.join(handler.response_buffer)
                handler.response_buffer.clear()

# Usage example:
for response_chunk in stream_prompt_response(client, thread.id, assistant.id, "I need to solve the equation `3x + 11 = 14`. Can you help me?"):
    print(response_chunk)