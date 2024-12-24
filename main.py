import os
from typing import Annotated

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, Header, Body, HTTPException, Request, status
from fastapi.responses import PlainTextResponse, StreamingResponse

from crawler.web_crawler import get_handouts, last_update
from llm.llm import message, update_handouts
from model.course import Course
from model.history import History
from model.message import Message
from model.user import User
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
def message_send(
    course_id: int,
    content: Annotated[str, Body(embed=True)],
    x_with_cookie: str = Header(),
) -> StreamingResponse:
    user_id = parse_account_from_cookie(x_with_cookie)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user ID in the cookie",
        )

    course = course_repository.get_course(course_id)
    if course is None or course.vector_store_id is None or course.assistant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course hans't been indexed",
        )

    user = user_repository.get_user(user_id)
    if user is None:
        user = User(id=user_id, histories=[])
        user_repository.create_user(user)

    history = list(filter(lambda e: e.course_id == course_id, user.histories))
    history = (
        History(course_id=course_id, history=[]) if len(history) == 0 else history[0]
    )

    def response():
        reply = ""
        for part in message(course.assistant_id, tuple(history.history), content):
            reply += part
            yield part
        history.history.append(Message(sender=1, content=content))
        history.history.append(Message(sender=0, content=reply))
        has_history = False
        for i, h in enumerate(user.histories):
            if h.course_id == course_id:
                user.histories[i] = history
                has_history = True
                break
        if not has_history:
            user.histories.append(history)
        user_repository.update_user(user)

    return StreamingResponse(response())


@app.post("/message/{course_id}/index")
def course_index(
    course_id: int,
    x_with_cookie: str = Header(),
) -> History:
    user_id = parse_account_from_cookie(x_with_cookie)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user ID in the cookie",
        )

    last_updated_time = last_update(x_with_cookie, course_id)
    if last_updated_time is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to fetch materials",
        )

    user = user_repository.get_user(user_id)
    if user is None:
        user = User(id=user_id, histories=[])
        user_repository.create_user(user)

    course = course_repository.get_course(course_id)
    if course is None:
        course = Course(id=course_id, updated_time=last_updated_time)
        course_repository.create_course(course)

    if course.updated_time >= last_updated_time:
        handouts = get_handouts(x_with_cookie, course_id)
        vector_store_id, assistant_id = update_handouts(
            course_id,
            tuple(handouts),
            course.vector_store_id,
            course.assistant_id,
        )

        course.vector_store_id = vector_store_id
        course.assistant_id = assistant_id
        course_repository.update_course(course)

    history = list(filter(lambda e: e.course_id == course_id, user.histories))
    history = (
        History(course_id=course_id, history=[]) if len(history) == 0 else history[0]
    )

    return history


def parse_account_from_cookie(cookie: str) -> str | None:
    for c in cookie.split(";"):
        key, value = tuple(map(lambda e: e.strip(), c.split("=")))
        if key == "account":
            return value
    return None
