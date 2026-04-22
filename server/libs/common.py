from typing import Dict, Optional
from libs.config import UtilsBase
from libs.websocket_client import WsClient
from libs.mxdict_database import MxDictDatabase
from libs.dict_database import DictDatabase


class Utils(UtilsBase):
    """通用工具类"""

    db = MxDictDatabase(UtilsBase.MXDICT_DATABASE_PATH)
    dict_db = DictDatabase(UtilsBase.DICT_DATABASE_PATH)
    iwin_ws_client: WsClient

    # 初始化服务
    # db = ChatDatabase(UtilsBase.DATABASE_PATH)
    # api = OpenAIChatAPI(db)
    # speaker = Speaker(UtilsBase.CONFIG, UtilsBase.VOICHAI_STORAGE_PATH)
    # recognizer = Recognizer(UtilsBase.CONFIG)

    # @staticmethod
    # def create_api() -> OpenAIChatAPI:
    #     db = ChatDatabase(UtilsBase.DATABASE_PATH)
    #     api = OpenAIChatAPI(db)
    #     return api

    # @staticmethod
    # def init_services():
    #     Utils.db = ChatDatabase(UtilsBase.DATABASE_PATH)
    #     Utils.api = OpenAIChatAPI(Utils.db)
    #     Utils.speaker = Speaker(UtilsBase.CONFIG, UtilsBase.VOICHAI_STORAGE_PATH)
    #     Utils.recognizer = Recognizer(UtilsBase.CONFIG)
