import json
import time
import threading
import asyncio
from websockets.asyncio.client import ClientConnection


from fastapi import WebSocket
from libs.log_config import logger
from libs.common import Utils
from libs.session_manager import SessionManager
from libs.mdict_searcher import MdictSearcher
from libs.websocket_client import WsClient


mdict_searcher = MdictSearcher()


class MessageHandler:
    """消息处理器，处理不同类型的WebSocket消息"""

    @staticmethod
    async def handle_command_message(command_type: str, data: dict) -> None:
        """处理命令消息"""
        if command_type == "":
            pass
        else:
            logger.warning(f"未知的命令类型: {command_type}")

    @staticmethod
    async def handle_iwin_message(ws: ClientConnection, data: str):
        """处理iWin消息"""
        try:
            message = json.loads(data)
            command_type = message["type"]
            if command_type == "client_id":
                client_id = message["data"]["client_id"]
                Utils.iwin_ws_client.set_client_id(client_id)
                logger.info(f"设置 iWin 客户端 ID: {client_id}")
            elif command_type == "toggle_floating_pin":
                session_id = message["data"]["session_id"]
                # connection_id = message["data"]["connection_id"]
                msg = {
                    "type": "toggle_floating_pin",
                    "data": {"is_pinned": message["data"]["is_pinned"]},
                }
                await SessionManager.broadcast_session(session_id, json.dumps(msg))
            else:
                logger.warning(f"未知的iWin命令类型: {command_type}")
        except Exception as e:
            logger.error(f"处理iWin消息时出错: {e}", exc_info=True)

    @staticmethod
    async def handle_session_message(
        websocket: WebSocket, session_id: int, connection_id: int, message_text: str
    ):
        """处理会话WebSocket消息"""
        try:
            message = json.loads(message_text)
            message_type = message["type"]

            handlers = {
                "toggle_floating_pin": MessageHandler._handle_toggle_floating_pin,
                "keyword_options_search": MessageHandler._handle_keyword_options_search,
                "lookup_keyword": MessageHandler._handle_lookup,
            }

            if message_type in handlers:
                await handlers[message_type](
                    websocket, session_id, connection_id, message
                )
            else:
                logger.warning(f"未知的会话消息类型: {message_type}")

        except Exception as e:
            logger.error(f"处理会话消息时出错: {e}", exc_info=True)

    @staticmethod
    async def _handle_toggle_floating_pin(
        websocket: WebSocket, session_id: int, connection_id: int, message: dict
    ):
        msg = {
            "type": "toggle_floating_pin",
            "data": {
                "session_id": session_id,
                "connection_id": connection_id,
            },
        }
        await Utils.iwin_ws_client.send(msg)

    @staticmethod
    async def _handle_keyword_options_search(
        websocket: WebSocket, session_id: int, connection_id: int, message: dict
    ):
        keyword = message["data"]["keyword"]
        search_method = message["data"]["search_method"]
        options = mdict_searcher.keyword_options_search(keyword, search_method)
        msg = {
            "type": "keyword_options_search",
            "data": {
                "keyword": keyword,
                "options": options,
            },
        }
        await SessionManager.send_msg_to_session_by_id(
            session_id, connection_id, json.dumps(msg)
        )

    @staticmethod
    async def _handle_lookup(
        websocket: WebSocket, session_id: int, connection_id: int, message: dict
    ):
        keyword = message["data"]["keyword"]
        results = mdict_searcher.mdx_lookup(keyword)
        msg = {
            "type": "lookup_keyword",
            "data": {
                "keyword": keyword,
                "result": results,
            },
        }
        await SessionManager.send_msg_to_session_by_id(
            session_id, connection_id, json.dumps(msg)
        )
