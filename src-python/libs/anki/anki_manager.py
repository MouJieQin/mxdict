# ========== Anki 管理器 ==========
import hashlib
import json
import os

from libs.config import UtilsBase
from libs.anki.anki_api import AnkiApi


class AnkiManager:


    html_back_content_prefix = """
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { margin: 0; padding: 0; }
                iframe { width: 100%; height: 85vh; border: none;  }
            </style>
        </head>
        <body>
    """

    def __init__(self):
        self.anki_api = AnkiApi()
        self.prefix_div='<div id="'
        self.suffix_div='</div>'
        self.__reload_anki_config()

    def _sync_anki_config(self):
        with open(UtilsBase.ANKI_CONFIG_FILE, mode="w", encoding="utf-8") as f:
            f.write(json.dumps(self.anki_config, ensure_ascii=False, indent=4))

    def __reload_anki_config(self):
        if os.path.exists(UtilsBase.ANKI_CONFIG_FILE):
            with open(UtilsBase.ANKI_CONFIG_FILE, "r") as f:
                self.anki_config = json.load(f)
        else:
            self.anki_config = {
                "format":{
                    "default":{
                        "front":'<p style="font-size: 32px; font-weight: bold;">{keyword}</p>',
                    }
                }
            }
            self._sync_anki_config()

    @staticmethod
    def get_str_unique_id(text: str) -> str:
        return hashlib.md5(text.strip().encode("utf-8")).hexdigest()
    
    def get_unique_id_from_front(self, front: str) -> str:
        start_index=front.find(self.prefix_div)
        end_index=front.find('">', start_index)
        if start_index==-1 or end_index==-1:
            return ""
        return front[start_index+len(self.prefix_div):end_index]
        
    def get_deck_cards_indexed_by_unique_id(self, deck_name: str) -> dict:
        cards = self.anki_api.get_deck_cards_info(deck_name)
        result = {}
        for card in cards:
            unique_id = self.get_unique_id_from_front(card["front"])
            result[unique_id] = card
        return result

    def update_words_to_anki(self, session_id: str, deck_name: str, words: list):
        """
        更新 Anki 中的单词
        :param deck_name: Anki 牌名
        :param words: 要更新的单词列表
        """
        self.__reload_anki_config()

        deck_format_config = self.anki_config["format"].get(deck_name, {})
        deck_front_format_config = deck_format_config.get("front", "")
        front_format_str =  deck_front_format_config or self.anki_config["format"]["default"]["front"]

        deck_cards = self.get_deck_cards_indexed_by_unique_id(deck_name)
        for word in words:
            unique_id = self.get_str_unique_id(word['word'])
            front_first_line=self.prefix_div + unique_id +'">'
            front_last_line =self.suffix_div
            front_content= front_format_str.format(keyword=word['word'])
            front=f"{front_first_line}\n{front_content}\n{front_last_line}"

            back = self.html_back_content_prefix
            back += f"<iframe src=\"http://localhost:9595/#/dict/{session_id}?keyword={word['word']}&env=anki\"></iframe>\n"
            back += "</body>\n</html>"

            note_id = deck_cards[unique_id]["noteId"] if unique_id in deck_cards else None
            self.anki_api.upsert_note_to_deck(deck_name, note_id, front, back)
