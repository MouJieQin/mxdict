from typing import Dict, Optional, Any
from pathlib import Path
import bisect
from Levenshtein import distance
import heapq


from libs.log_config import logger
from libs.mdict_query.mdict_query import IndexBuilder
from libs.config import UtilsBase


class MdictSearcher:
    def __init__(self):
        self._indexBuilders: Dict[str, IndexBuilder] = {}
        self._all_words_sorted: list[str] = []
        self._build_mdxs_index()

    def _build_mdxs_index(self):
        """构建所有词典索引"""
        logger.info("开始构建所有词典索引")
        all_words = []
        for dict_name, dict_info in UtilsBase.DICT_INFO.items():
            logger.info(f"词典 {dict_name} 的路径: {dict_info['path']}")
            logger.info(f"词典 {dict_name} 的 CSS 文件路径: {dict_info['css']}")
            logger.info(f"词典 {dict_name} 的 JS 文件路径: {dict_info['js']}")
            logger.info(f"词典 {dict_name} 的数据目录路径: {dict_info['data']}")
            logger.info(f"词典 {dict_name} 的索引构建开始")
            self._indexBuilders[dict_name] = IndexBuilder(dict_info["path"])
            logger.info(f"词典 {dict_name} 的索引构建完成")
            all_words.extend(self._indexBuilders[dict_name].get_mdx_keys())

        self._all_words_sorted = sorted(set(all_words))
        logger.info(f"所有词典索引构建完成，共 {len(self._all_words_sorted)} 个单词")

    def mdx_lookup(
        self, keyword: str, ignorecase: Optional[bool] = None
    ) -> Dict[str, Dict[str, list[str]]]:
        """查询所有词典"""
        results = {}
        for dict_name, indexBuilder in self._indexBuilders.items():
            res = indexBuilder.mdx_lookup(keyword, ignorecase)
            if res:
                result = []
                self._hand_link_word(result, indexBuilder, res, [keyword], ignorecase)
                results[dict_name] = result
        return results

    def _hand_link_word(
        self,
        result: list[str],
        indexBuilder: IndexBuilder,
        cur_result: list[str],
        words_show: list[str],
        ignorecase: Optional[bool] = None,
    ):
        """处理重定向单词"""
        for i in range(len(cur_result)):
            item = cur_result[i]
            if "@@@LINK=" not in item:
                result.append(item)
            else:
                redirect_word = item.split("@@@LINK=")[1].strip()
                if redirect_word not in words_show:
                    words_show.append(redirect_word)
                    res_redirect = indexBuilder.mdx_lookup(redirect_word, ignorecase)
                    if res_redirect:
                        self._hand_link_word(
                            result, indexBuilder, res_redirect, words_show, ignorecase
                        )

    def keyword_options_search(self, keyword: str, search_method: str, limit=20):
        """关键词选项搜索"""
        if search_method == "prefix_search":
            return self.prefix_search(self._all_words_sorted, keyword, limit)
        elif search_method == "contains_search":
            return self.contains_search(self._all_words_sorted, keyword, limit)
        elif search_method == "fuzzy_search":
            return self.fuzzy_search(self._all_words_sorted, keyword, limit)
        elif search_method == "fuzzy_contains_search":
            return self.fuzzy_contains_search(self._all_words_sorted, keyword, limit)
        else:
            raise ValueError("Invalid search method")

    @staticmethod
    def prefix_search(words_sorted: list[str], keyword: str, limit=20):
        """前缀匹配：以 xxx 开头"""
        idx = bisect.bisect_left(words_sorted, keyword)
        result = []

        for word in words_sorted[idx:]:
            if word.startswith(keyword):
                result.append(word)
                if len(result) >= limit:
                    break
            else:
                break  # 排序后不匹配就直接退出，超快

        return result

    @staticmethod
    def contains_search(words: list[str], keyword: str, limit=20):
        """包含匹配：单词里含有 xxx"""
        result = []
        keyword = keyword.lower()  # 不区分大小写

        for word in words:
            if keyword in word.lower():
                result.append(word)
                if len(result) >= limit:
                    break

        return result

    @staticmethod
    def fuzzy_search(words: list[str], keyword: str, limit=20):
        """
        模糊搜索：找最相似的前 N 个
        越小越像：0=完全一样
        """
        # 用堆取 TopN，比全排序快 10 倍以上
        heap = []
        keyword = keyword.lower()

        for word in words:
            word_lower = word.lower()
            dist = distance(keyword, word_lower)

            # 推入堆（距离，单词）
            heapq.heappush(heap, (dist, word))

        # 取出前 limit 个
        result = [word for _, word in heapq.nsmallest(limit, heap)]
        return result

    @staticmethod
    def fuzzy_contains_search(words: list[str], keyword: str, limit=20):
        """
        模糊包含搜索：找最相似的前 N 个
        """
        # 用堆取 TopN，比全排序快 10 倍以上
        heap = []
        keyword = keyword.lower()

        for word in words:
            word_lower = word.lower()
            if keyword not in word_lower:
                continue
            dist = distance(keyword, word_lower)

            # 推入堆（距离，单词）
            heapq.heappush(heap, (dist, word))

        # 取出前 limit 个
        result = [word for _, word in heapq.nsmallest(limit, heap)]
        return result
