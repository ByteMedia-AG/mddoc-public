from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Set up the FTS5 index and triggers for the doc_doc table (SQLite only)'

    def handle(self, *args, **options):
        statements = [
            "DROP TABLE IF EXISTS doc_doc_idx;",
            "DROP TRIGGER IF EXISTS doc_doc_ai;",
            "DROP TRIGGER IF EXISTS doc_doc_ad;",
            "DROP TRIGGER IF EXISTS doc_doc_au;",
            """
            CREATE VIRTUAL TABLE doc_doc_idx USING fts5(
                id, title, description, text, tag, uri, updated_at, deleted_at,
                is_archived, successor_id, time, created_at,
                is_flagged, last_settlement, has_unsettled_tr,
                content=doc_doc, content_rowid=id
            );
            """,
            """
            INSERT INTO doc_doc_idx (
                rowid, title, description, text, tag, uri
            )
            SELECT id, title, description, text, tag, uri FROM doc_doc;
            """,
            """
            CREATE TRIGGER doc_doc_ai AFTER INSERT ON doc_doc BEGIN
                INSERT INTO doc_doc_idx(rowid, title, description, text, tag, uri)
                VALUES (new.id, new.title, new.description, new.text, new.tag, new.uri);
            END;
            """,
            """
            CREATE TRIGGER doc_doc_ad AFTER DELETE ON doc_doc BEGIN
                INSERT INTO doc_doc_idx(doc_doc_idx, rowid, title, description, text, tag, uri)
                VALUES('delete', old.id, old.title, old.description, old.text, old.tag, old.uri);
            END;
            """,
            """
            CREATE TRIGGER doc_doc_au AFTER UPDATE ON doc_doc BEGIN
                INSERT INTO doc_doc_idx(doc_doc_idx, rowid, title, description, text, tag, uri)
                VALUES('delete', old.id, old.title, old.description, old.text, old.tag, old.uri);
                INSERT INTO doc_doc_idx(rowid, title, description, text, tag, uri)
                VALUES (new.id, new.title, new.description, new.text, new.tag, new.uri);
            END;
            """
        ]

        with connection.cursor() as cursor:
            for stmt in statements:
                self.stdout.write(self.style.NOTICE(f"Executing:\n{stmt.strip()}"))
                cursor.executescript(stmt) if ';' in stmt else cursor.execute(stmt)

        self.stdout.write(self.style.SUCCESS("FTS5 index and triggers set up successfully."))
