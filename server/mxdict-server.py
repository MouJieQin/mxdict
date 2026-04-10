#!/usr/bin/env python3
# _*_coding:utf-8_*_

import json
import os
import time

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


# 配置应用
app = FastAPI(title="Dictionary API Server", description="WebSocket-based dictionary API server")
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


# 启动应用
if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    # 初始化会话
    # SessionManager.initialize_sessions()

    # 启动服务器
    uvicorn.run(
        app="mxdict-server:app",
        host="localhost",
        port=5959,
        reload=False,
    )
