import json
import time
from typing import Optional
from fastapi import WebSocket
from libs.log_config import logger
from libs.common import Utils


class SessionManager:
    """会话管理器，负责会话的创建、删除、配置更新等操作"""

    @staticmethod
    async def send_msg_to_session_by_id(
        session_id: int, connection_id: int, message: str
    ):
        """向特定会话的WebSocket连接发送消息"""
        if (
            session_id not in Utils.session_websockets
            or connection_id not in Utils.session_websockets[session_id]
        ):
            return

        websocket = Utils.session_websockets[session_id][connection_id]
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"会话广播错误: {e}")
            del Utils.session_websockets[session_id][connection_id]

    @staticmethod
    async def send_dict_info_to_session(session_id: int, connection_id: int):
        """向特定会话的WebSocket连接发送词典信息"""
        msg = {
            "type": "dict_info",
            "data": Utils.DICT_INFO,
        }
        await SessionManager.send_msg_to_session_by_id(
            session_id, connection_id, json.dumps(msg)
        )

    @staticmethod
    async def send_session_config_to_session(session_id: int, connection_id: int):
        """向特定会话的WebSocket连接发送会话配置"""
        config = Utils.db.get_session_config(session_id)
        if config is None:
            return
        msg = {
            "type": "session_config",
            "data": {"config": config},
        }
        await SessionManager.send_msg_to_session_by_id(
            session_id, connection_id, json.dumps(msg)
        )

    @staticmethod
    async def broadcast_session(session_id: int, message: str):
        """向特定会话的所有WebSocket连接广播消息"""
        session_id = int(session_id)
        if session_id not in Utils.session_websockets:
            return

        invalid_keys = []
        for key, websocket in Utils.session_websockets[session_id].items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"会话广播错误: {e}")
                invalid_keys.append(key)

        # 移除无效连接
        for key in invalid_keys:
            del Utils.session_websockets[session_id][key]
