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
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text):
        yield f"\nassistant > "

    @override
    def on_text_delta(self, delta, snapshot):
        yield delta.value

    def on_tool_call_created(self, tool_call):
        yield f"\nassistant > {tool_call.type}\n"

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                yield delta.code_interpreter.input
            if delta.code_interpreter.outputs:
                yield f"\n\noutput >"
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        yield f"\n{output.logs}"

def stream_run(client, thread_id, assistant_id):
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please address the user as Jane Doe. The user has a premium account.",
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

# Example of calling the function
def main():
    for x in stream_run(client, thread.id, assistant.id):
        print(x)

if __name__ == "__main__":
    main()
