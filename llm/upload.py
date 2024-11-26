
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
# Create a vector store caled "Financial Statements"
vector_store = client.beta.vector_stores.create(name="upload_test")
 
# Ready the files for upload to OpenAI
file_paths = ["llm/AI智慧學習挑戰賽簡章.pdf"]
file_streams = [open(path, "rb") for path in file_paths]
 
# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)
 
# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

assistant = client.beta.assistants.update(
  assistant_id='asst_57YGAaJrxBukAdPd4ZZBN7wo',
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)