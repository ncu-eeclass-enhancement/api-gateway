import asyncio

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import PlainTextResponse, StreamingResponse

app = FastAPI()


@app.get("/")
def root(request: Request) -> PlainTextResponse:
    return f"Please refer to {request.base_url}docs or {request.base_url}redoc for the API document."


@app.post("/message/{course_id}/send")
async def message_send(course_id: str, request: Request) -> StreamingResponse:
    cookie = request.headers.get("X-With-Cookie")
    if cookie is None:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing necessary headers",
        )

    async def response():
        for c in f"Hello, {course_id}":
            await asyncio.sleep(0.25)
            yield f"{c}\r\n"

    return StreamingResponse(response())
