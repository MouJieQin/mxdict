#!/usr/bin/env python3
# _*_coding:utf-8_*_

import json
import os
import time
import asyncio

from fastapi import (
    FastAPI,
    UploadFile,
    Form,
    File,
    Path,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from starlette.responses import FileResponse
from pathlib import Path


# from libs.mdict_query.mdict_query import IndexBuilder
from libs.log_config import logger
from libs.mdict_searcher import MdictSearcher
from libs.common import Utils
from libs.session_manager import SessionManager
from libs.message_handler import MessageHandler
from libs.websocket_client import WsClient



# 配置应用
app = FastAPI(
    title="Dictionary API Server", description="WebSocket-based dictionary API server"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/download")
async def download(path: str):
    logger.info(f"download path: {path}")
    # path = Utils.DATA_PATH + path
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail="Not a file or does not exist")

    fr = FileResponse(
        path=path,
        filename=Path(path).name,
    )
    return fr


class CommandRequest(BaseModel):
    type: str
    data: dict


@app.post("/api/command")
async def command_command(request: CommandRequest):
    logger.info(f"command command: {request.type}")
    logger.info(f"command data: {request.data}")
    res = await MessageHandler.handle_command_message(request.type, request.data)
    return {"success": res}


@app.websocket("/ws/dictionary/session")
async def dictionary_session_websocket_endpoint(websocket: WebSocket):
    """Dictionary Session WebSocket端点"""
    await websocket.accept()
    connection_id = int(time.time() * 1000)
    Utils.session_websockets[connection_id] = websocket

    try:
        await SessionManager.send_dict_info_to_session(connection_id)
        while True:
            data = await websocket.receive_text()
            await MessageHandler.handle_session_message(websocket, connection_id, data)

    except WebSocketDisconnect:
        logger.info(f"SPA WebSocket断开连接")
    except Exception as e:
        logger.error(f"SPA WebSocket错误: {e}", exc_info=True)
    finally:
        if connection_id in Utils.spa_websockets:
            del Utils.spa_websockets[connection_id]





# ==============================================
# WebSocket Client 连接 iWin 服务器
# ==============================================
# 全局单例（整个程序共用一个连接）
iwin_ws_client = WsClient("ws://localhost:9999/ws/mxdict", MessageHandler.handle_iwin_message)



# ==============================================
# 启动应用（同时启动 WebSocket 客户端）
# ==============================================
async def main_server():
    # 1. 初始化
    os.chdir(os.path.dirname(__file__))

    # 2. 后台启动 Electron WebSocket 客户端
    asyncio.create_task(iwin_ws_client.connect())

    # 3. 启动 FastAPI 服务器
    config = uvicorn.Config(
        app="mxdict-server:app",
        host="localhost",
        port=5959,
        reload=False,
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main_server())


# # 启动应用
# if __name__ == "__main__":
#     os.chdir(os.path.dirname(__file__))
#     # 初始化会话
#     # SessionManager.initialize_sessions()

#     # 启动服务器
#     uvicorn.run(
#         app="mxdict-server:app",
#         host="localhost",
#         port=5959,
#         reload=False,
#     )
