"""
Dedupe Cache (MVP)
SQLite-based cache to filter duplicates by URL/hash and user_id.
Supports multi-user, persistent deduplication for Orchestrator and Excel Exporter.
"""
import sqlite3
from pathlib import Path
from typing import Optional

class DedupeCache:
    def dedupe(self, df, user_id_col='user_id', url_col='url', jobid_col='JobID'):
        # Remove duplicates by JobID or URL
        if jobid_col in df.columns:
            df = df.drop_duplicates(subset=[jobid_col])
        elif url_col in df.columns:
            df = df.drop_duplicates(subset=[url_col])
        return df
    def __init__(self, db_path: str = "dedupe_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dedupe (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    url TEXT,
                    hash TEXT,
                    UNIQUE(user_id, url, hash)
                )
            """)
            conn.commit()

    def is_duplicate(self, user_id: str, url: Optional[str] = None, hash_: Optional[str] = None) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            if url and hash_:
                cur.execute("SELECT 1 FROM dedupe WHERE user_id=? AND (url=? OR hash=?)", (user_id, url, hash_))
            elif url:
                cur.execute("SELECT 1 FROM dedupe WHERE user_id=? AND url=?", (user_id, url))
            elif hash_:
                cur.execute("SELECT 1 FROM dedupe WHERE user_id=? AND hash=?", (user_id, hash_))
            else:
                return False
            return cur.fetchone() is not None

    def add(self, user_id: str, url: Optional[str] = None, hash_: Optional[str] = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR IGNORE INTO dedupe (user_id, url, hash) VALUES (?, ?, ?)", (user_id, url, hash_))
            conn.commit()

    def clear(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM dedupe")
            conn.commit()

# Example usage:
# cache = DedupeCache()
# if not cache.is_duplicate(user_id, url, hash_):
#     cache.add(user_id, url, hash_)
#     ...process...
