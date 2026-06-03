"""
DevMirror — MongoDB client for chat history, agent sessions, and API cache.
Used alongside SQLite (user auth) to store agent-specific data.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI", "")

_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is not None:
        return _db
    if not MONGODB_URI:
        logger.warning("MONGODB_URI not set — MongoDB features disabled")
        return None
    try:
        from pymongo import MongoClient
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        _db = _client["devmirror"]
        logger.info("MongoDB connected")
        return _db
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None


# ── Chat history ───────────────────────────────────────────────────────────────

def save_chat_message(user_id: int, role: str, content: str, tool_calls: Optional[list] = None) -> None:
    db = _get_db()
    if db is None:
        return
    try:
        db["chat_history"].insert_one({
            "user_id":    user_id,
            "role":       role,
            "content":    content,
            "tool_calls": tool_calls or [],
            "timestamp":  datetime.utcnow(),
        })
    except Exception as e:
        logger.error(f"save_chat_message failed: {e}")


def get_chat_history(user_id: int, limit: int = 20) -> list[dict]:
    db = _get_db()
    if db is None:
        return []
    try:
        cursor = db["chat_history"].find(
            {"user_id": user_id},
            {"_id": 0},
        ).sort("timestamp", -1).limit(limit)
        return list(reversed(list(cursor)))
    except Exception as e:
        logger.error(f"get_chat_history failed: {e}")
        return []


def clear_chat_history(user_id: int) -> None:
    db = _get_db()
    if db is None:
        return
    try:
        db["chat_history"].delete_many({"user_id": user_id})
    except Exception as e:
        logger.error(f"clear_chat_history failed: {e}")


# ── Agent sessions (tool call traces for the reasoning panel) ─────────────────

def save_agent_session(user_id: int, question: str, tool_calls: list[dict], answer: str) -> None:
    db = _get_db()
    if db is None:
        return
    try:
        db["agent_sessions"].insert_one({
            "user_id":    user_id,
            "question":   question,
            "tool_calls": tool_calls,
            "answer":     answer,
            "timestamp":  datetime.utcnow(),
        })
    except Exception as e:
        logger.error(f"save_agent_session failed: {e}")


def get_last_agent_session(user_id: int) -> Optional[dict]:
    db = _get_db()
    if db is None:
        return None
    try:
        doc = db["agent_sessions"].find_one(
            {"user_id": user_id},
            {"_id": 0},
            sort=[("timestamp", -1)],
        )
        return doc
    except Exception as e:
        logger.error(f"get_last_agent_session failed: {e}")
        return None


# ── API response cache (supplement the in-memory cache) ───────────────────────

def cache_set(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    db = _get_db()
    if db is None:
        return
    try:
        db["api_cache"].replace_one(
            {"key": key},
            {
                "key":        key,
                "value":      value,
                "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds),
            },
            upsert=True,
        )
    except Exception as e:
        logger.error(f"cache_set failed: {e}")


def cache_get(key: str) -> Optional[Any]:
    db = _get_db()
    if db is None:
        return None
    try:
        doc = db["api_cache"].find_one({"key": key, "expires_at": {"$gt": datetime.utcnow()}})
        return doc["value"] if doc else None
    except Exception as e:
        logger.error(f"cache_get failed: {e}")
        return None


def is_connected() -> bool:
    return _get_db() is not None
