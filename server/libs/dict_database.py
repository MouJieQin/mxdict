import sqlite3
import json
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from libs.log_config import logger


class DictDatabase:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # 使用字典形式返回结果
        self._setup_foreign_keys()
        self._create_tables()

    def _setup_foreign_keys(self) -> None:
        """确保外键约束启用"""
        with self.conn:
            self.conn.execute("PRAGMA foreign_keys = ON")
            # 验证约束是否启用
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA foreign_keys")
            if cursor.fetchone()[0] != 1:
                raise RuntimeError("无法启用外键约束")

    def _create_tables(self) -> None:
        """创建会话和消息表"""
        with self.conn:
            cursor = self.conn.cursor()
            # 创建会话表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY,
                    config TEXT
                )
            """
            )

    def create_session(self, session_id: int, config_config: Dict[str, Any]):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (id, config) VALUES (?, ?)",
                (session_id, json.dumps(config_config, ensure_ascii=False)),
            )

    def get_session_config(self, session_id: int) -> Optional[Dict[str, Any]]:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT config FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["config"])
            return None

    def is_session_exist(self, session_id: int) -> bool:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
            return bool(cursor.fetchone())

    def update_session_config(self, session_id: int, config_config: Dict[str, Any]):
        if not self.is_session_exist(session_id):
            self.create_session(session_id, config_config)
            return
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE sessions SET config = ? WHERE id = ?",
                (json.dumps(config_config, ensure_ascii=False), session_id),
            )

    def close(self) -> None:
        self.conn.close()
