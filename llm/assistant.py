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
  content="hello"#"I need to solve the equation `3x + 11 = 14`. Can you help me?"
)

from typing_extensions import override
from openai import AssistantEventHandler

def stream_response(prompt: str, thread_id: str, assistant_id: str, client):
    class EventHandler(AssistantEventHandler):
        @override
        def on_text_created(self, text) -> None:
            yield {"type": "text_created", "content": text}

        @override
        def on_text_delta(self, delta, snapshot):
            yield {"type": "text_delta", "content": delta.value}

        @override
        def on_tool_call_created(self, tool_call):
            yield {"type": "tool_call_created", "content": tool_call.type}

        @override
        def on_tool_call_delta(self, delta, snapshot):
            if delta.type == 'code_interpreter':
                if delta.code_interpreter.input:
                    yield {"type": "tool_input", "content": delta.code_interpreter.input}
                if delta.code_interpreter.outputs:
                    outputs = []
                    for output in delta.code_interpreter.outputs:
                        if output.type == "logs":
                            outputs.append(output.logs)
                    yield {"type": "tool_outputs", "content": outputs}

    # Stream the response using the provided prompt
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=prompt,
        event_handler=EventHandler(),
    ) as stream:
        for event in stream:
            yield event

for x in stream_response("hi", thread.id, assistant.id, client):
    print(x)
    
# stream_response("hi", thread.id, assistant.id, client)