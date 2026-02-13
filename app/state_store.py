import sqlite3
import time


SCHEMA = """
CREATE TABLE IF NOT EXISTS processed (
  signal_id TEXT PRIMARY KEY,
  processed_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS kv (
  k TEXT PRIMARY KEY,
  v TEXT NOT NULL
);
"""


class StateStore:
    def __init__(self, path: str):
        self.path = path
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.executescript(SCHEMA)
        self._conn.commit()
        # default mode
        if self.kv_get("mode") is None:
            self.kv_set("mode", "enabled")

    def seen(self, signal_id: str) -> bool:
        cur = self._conn.execute("SELECT 1 FROM processed WHERE signal_id = ?", (signal_id,))
        return cur.fetchone() is not None

    def mark_seen(self, signal_id: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO processed(signal_id, processed_at) VALUES (?, ?)",
            (signal_id, time.time()),
        )
        self._conn.commit()

    def count_processed(self) -> int:
        cur = self._conn.execute("SELECT COUNT(*) FROM processed")
        return int(cur.fetchone()[0])

    def kv_get(self, k: str):
        cur = self._conn.execute("SELECT v FROM kv WHERE k = ?", (k,))
        row = cur.fetchone()
        return row[0] if row else None

    def kv_set(self, k: str, v: str) -> None:
        self._conn.execute("INSERT OR REPLACE INTO kv(k, v) VALUES (?, ?)", (k, v))
        self._conn.commit()

    def get_mode(self) -> str:
        return self.kv_get("mode") or "enabled"

    def set_mode(self, mode: str) -> None:
        self.kv_set("mode", mode)
