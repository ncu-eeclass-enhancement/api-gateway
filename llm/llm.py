import os
from typing import Any, Generator, Iterable

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.beta import Assistant, VectorStore
from openai.types.beta.threads import MessageDeltaEvent, TextDeltaBlock
from pydantic import BaseModel, Field

from model.handout import Handout
from model.message import Message

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")
AI_MODEL = os.getenv("AI_MODEL")

client = OpenAI(api_key=OPENAI_KEY)


class _File(BaseModel):
    id: str | None = Field(None)
    filename: str = Field("")
    content: bytes | None = Field(None)


def update_handouts(
    course_id: int,
    handouts: tuple[Handout],
    vector_store_id: str = None,
    assistant_id: str = None,
) -> tuple[str, str]:
    """
    Returns the vector store ID and assistant ID.
    """
    if vector_store_id is None:
        vector_store = create_vector_store(course_id)
        vector_store_id = vector_store.id

    if assistant_id is None:
        assistant = create_assistant(vector_store_id, description=str(course_id))
        assistant_id = assistant.id

    files = list(map(lambda e: _File(filename=e.filename, content=e.content), handouts))
    upload_and_replace_files(files, vector_store_id)

    return (vector_store_id, assistant_id)


def message(
    assistant_id: str,
    history: tuple[Message],
    content: str,
) -> Generator[str, Any, None]:
    messages = list(
        map(
            lambda e: {
                "role": "assistant" if e.sender == 0 else "user",
                "content": e.content,
            },
            history,
        )
    )
    messages.append({"role": "user", "content": content})
    with client.beta.threads.create_and_run_stream(
        assistant_id=assistant_id,
        thread={"messages": messages},
    ) as stream:
        for event in stream:
            if isinstance(event.data, MessageDeltaEvent):
                content = event.data.delta.content[0]
                if isinstance(content, TextDeltaBlock):
                    yield event.data.delta.content[0].text.value


def upload_and_replace_files(files: Iterable[_File], vector_store_id: str):
    original_file_ids = map(
        lambda e: e.id,
        client.beta.vector_stores.files.list(vector_store_id, limit=100).data,
    )
    if len(files) > 0:
        client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id,
            files=map(lambda e: (e.filename, e.content), files),
        )
    for original_file_id in original_file_ids:
        client.files.delete(original_file_id)


def create_vector_store(course_id: int) -> VectorStore:
    vector_store = client.beta.vector_stores.create(name=f"course_{course_id}")
    return vector_store


def create_assistant(vector_store_id: str, description: str) -> Assistant:
    assistant = client.beta.assistants.create(
        model=AI_MODEL,
        name="Course Assistant",
        description=description,
        instructions="You are a course assistant who will find answers from the handouts you have and reply the question I asked. If the answer cannot be found in the documents, please do not make things up.",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    return assistant
