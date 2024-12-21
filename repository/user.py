from psycopg2.extensions import connection
from psycopg2.errors import DuplicateObject


class UserRepository:
    def __init__(self, db: connection):
        self.db = db
        self._create_table()

    def _create_table(self):
        with self.db.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    CREATE TYPE public.message_t AS (
                        role INTEGER,
                        content TEXT
                    );
                    """
                )
            except DuplicateObject:
                pass
            self.db.commit()
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public.user (
                    id INTEGER PRIMARY KEY,
                    history message_t[]
                );
                """
            )
            self.db.commit()
