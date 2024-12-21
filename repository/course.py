from psycopg2.errors import DuplicateObject
from psycopg2.extensions import connection

from model.course import Course


class CourseRepository:
    def __init__(self, db: connection):
        self.db = db
        self._create_table()

    def _create_table(self):
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public.handout (
                    id SERIAL PRIMARY KEY,
                    filename TEXT,
                    content BYTEA,
                    updated_time TIMESTAMP
                );
                """
            )
            self.db.commit()
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public.course (
                    id int4 NOT NULL PRIMARY KEY,
                    handouts _int4 NOT NULL,
                    vector_store_id varchar(27) NULL,
                    assistant_id varchar(29) NULL,
                    updated_time timestamp NOT NULL
                );
                """
            )
            self.db.commit()

    def get_course(self, course_id: int) -> Course | None:
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM public.course WHERE id = %s;
                """,
                (course_id,),
            )
            row = cursor.fetchone()
        return (
            None
            if row is None
            else Course(
                id=row[0],
                handouts=row[1],
                vector_store_id=row[2],
                assistant_id=row[3],
                updated_time=row[4],
            )
        )

    def create_course(self, course: Course):
        with self.db.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO public.course (id, handouts, vector_store_id, assistant_id, updated_time)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        course.id,
                        course.handouts,
                        course.vector_store_id,
                        course.assistant_id,
                        course.updated_time,
                    ),
                )
                self.db.commit()
            except DuplicateObject:
                pass

    def update_course(self, course: Course):
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE public.course
                SET handouts = %s, vector_store_id = %s, assistant_id = %s, updated_time = %s
                WHERE id = %s;
                """,
                (
                    course.handouts,
                    course.vector_store_id,
                    course.assistant_id,
                    course.updated_time,
                    course.id,
                ),
            )
            self.db.commit()
