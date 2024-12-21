import asyncio
import os

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import PlainTextResponse, StreamingResponse

from crawler.web_crawler import get_handouts, last_update
from llm.llm import update_handouts
from model.course import Course
from model.handout import Handout
from model.message import History
from repository.course import CourseRepository
from repository.user import UserRepository

load_dotenv()

DB_PASSWORD = os.getenv("DB_PASSWORD")

app = FastAPI()
db = psycopg2.connect(
    f"host=127.0.0.1 port=5432 dbname=postgres user=postgres password={DB_PASSWORD}"
)

course_repository = CourseRepository(db)
user_repository = UserRepository(db)


@app.get("/")
def root(request: Request) -> PlainTextResponse:
    return f"Please refer to {request.base_url}docs or {request.base_url}redoc for the API document."


@app.post("/message/{course_id}/send")
async def message_send(
    course_id: int,
    x_with_cookie: str = Header(),
) -> StreamingResponse:
    async def response():
        for c in f"Hello, {course_id}":
            await asyncio.sleep(0.25)
            yield f"{c}\r\n"

    return StreamingResponse(response())


@app.post("/message/{course_id}/index")
async def course_index(
    course_id: int,
    x_with_cookie: str = Header(),
) -> History:
    last_updated_time = last_update(x_with_cookie, course_id)
    if last_updated_time is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to fetch materials",
        )

    course = course_repository.get_course(course_id)
    if course is None:
        course = Course(id=course_id, updated_time=last_updated_time)
        course_repository.create_course(course)

    handouts = get_handouts(x_with_cookie, course_id)
    vector_store_id, assistant_id = update_handouts(
        course_id,
        handouts,
        course.vector_store_id,
        course.assistant_id,
    )

    course.vector_store_id = vector_store_id
    course.assistant_id = assistant_id
    course_repository.update_course(course)

    return History(history=[])
