import json
import time
import threading
import asyncio

from fastapi import WebSocket
from libs.log_config import logger
from libs.common import Utils
from libs.session_manager import SessionManager
from libs.mdict_searcher import MdictSearcher


mdict_searcher = MdictSearcher()


class MessageHandler:
    """消息处理器，处理不同类型的WebSocket消息"""

    @staticmethod
    async def handle_session_message(
        websocket: WebSocket, session_id: int, message_text: str
    ):
        """处理会话WebSocket消息"""
        try:
            message = json.loads(message_text)
            message_type = message["type"]

            handlers = {
                "toggle_float_pin": MessageHandler._handle_toggle_float_pin,
                "keyword_options_search": MessageHandler._handle_keyword_options_search,
                "lookup_keyword": MessageHandler._handle_lookup,
            }

            if message_type in handlers:
                await handlers[message_type](websocket, session_id, message)
            else:
                logger.warning(f"未知的会话消息类型: {message_type}")

        except Exception as e:
            logger.error(f"处理会话消息时出错: {e}", exc_info=True)

    @staticmethod
    async def _handle_toggle_float_pin(
        websocket: WebSocket, session_id: int, message: dict
    ):
        url = "http://localhost:3999" + message["data"]["full_path"]
        msg = {
            "type": "toggle_float_pin",
            "data": {
                "url": url,
                "session_id": session_id,
            },
        }
        await SessionManager.send_msg_to_session_by_id(session_id, json.dumps(msg))

    @staticmethod
    async def _handle_keyword_options_search(
        websocket: WebSocket, session_id: int, message: dict
    ):
        keyword = message["data"]["keyword"]
        options = mdict_searcher.keyword_options_search(keyword)
        msg = {
            "type": "keyword_options_search",
            "data": {
                "keyword": keyword,
                "options": options,
            },
        }
        await SessionManager.send_msg_to_session_by_id(session_id, json.dumps(msg))

    @staticmethod
    async def _handle_lookup(websocket: WebSocket, session_id: int, message: dict):
        keyword = message["data"]["keyword"]
        results = mdict_searcher.mdx_lookup(keyword)
        msg = {
            "type": "lookup_keyword",
            "data": {
                "keyword": keyword,
                "result": results,
            },
        }
        await SessionManager.send_msg_to_session_by_id(session_id, json.dumps(msg))
