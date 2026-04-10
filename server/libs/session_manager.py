import json
import time
from typing import Optional
from fastapi import WebSocket
from libs.log_config import logger
from libs.common import Utils


class SessionManager:
    """会话管理器，负责会话的创建、删除、配置更新等操作"""

    @staticmethod
    async def send_msg_to_session_by_id(connection_id: int, message: str):
        """向特定会话的WebSocket连接发送消息"""
        if connection_id not in Utils.session_websockets:
            return

        websocket = Utils.session_websockets[connection_id]
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"会话广播错误: {e}")
            del Utils.session_websockets[connection_id]

    @staticmethod
    async def send_dict_info_to_session(connection_id: int):
        """向特定会话的WebSocket连接发送词典信息"""
        msg={
            "type": "dict_info",
            "data": Utils.DICT_INFO,
        }
        await SessionManager.send_msg_to_session_by_id(
            connection_id, json.dumps(msg)
        )
