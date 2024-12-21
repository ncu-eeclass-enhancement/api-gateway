import json

from psycopg2.errors import DuplicateObject
from psycopg2.extensions import connection

from model.history import History
from model.message import Message
from model.user import User


class UserRepository:
    def __init__(self, db: connection):
        self.db = db
        self._create_table()

    def _create_table(self):
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public."user" (
                    id varchar(10) NOT NULL PRIMARY KEY,
                    histories json DEFAULT '[]'::json NOT NULL
                );
                """
            )
            self.db.commit()

    def get_user(self, user_id: int) -> User | None:
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM public."user" WHERE id = %s;
                """,
                (user_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        histories = list(
            map(
                lambda e: History(
                    course_id=e["course_id"],
                    history=list(map(lambda m: Message(**m), e["history"])),
                ),
                row[1],
            )
        )
        return User(id=row[0], histories=histories)

    def create_user(self, user: User):
        with self.db.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO public."user" (id, histories)
                    VALUES (%s, %s);
                    """,
                    (
                        user.id,
                        json.dumps(list(map(lambda e: e.model_dump(), user.histories))),
                    ),
                )
                self.db.commit()
            except DuplicateObject:
                pass

    def update_user(self, user: User):
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE public."user"
                SET histories = %s
                WHERE id = %s;
                """,
                (
                    json.dumps(list(map(lambda e: e.model_dump(), user.histories))),
                    user.id,
                ),
            )
            self.db.commit()
