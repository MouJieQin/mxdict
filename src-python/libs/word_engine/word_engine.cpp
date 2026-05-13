#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
#include <queue>
#include <cctype>

namespace py = pybind11;
using namespace std;

// 快速小写转换
string to_lower(const string &s)
{
    string res;
    res.reserve(s.size());
    for (unsigned char c : s)
        res += tolower(c);
    return res;
}

// 极简 Levenshtein 距离（C 版超快）
int levenshtein(const char *a, const char *b)
{
    int m = 0, n = 0;
    const char *pa = a, *pb = b;
    while (*pa++)
        m++;
    while (*pb++)
        n++;
    vector<int> dp(n + 1);
    for (int i = 0; i <= n; i++)
        dp[i] = i;
    for (int i = 1; i <= m; i++)
    {
        int prev = dp[0];
        dp[0] = i;
        for (int j = 1; j <= n; j++)
        {
            int temp = dp[j];
            if (a[i - 1] == b[j - 1])
                dp[j] = prev;
            else
                dp[j] = 1 + min({prev, dp[j], dp[j - 1]});
            prev = temp;
        }
    }
    return dp[n];
}

// ====================== 核心类 ======================
class WordStorage
{
private:
    // 所有词典：dict_name => 单词数组
    unordered_map<string, vector<string>> _dict_words;

    // 激活的单词视图（不复制数据，只是指针/引用合集）
    vector<const string *> _active_view;

public:
    // 1. 添加词典单词（Python 只调用一次）
    void add_dict(const string &dict_name, const vector<string> &words)
    {
        _dict_words[dict_name] = words;
    }

    // 2. 设置当前激活的词典（用户切换词典时调用）
    // 关键：瞬间完成，不复制任何单词！
    void set_active_dicts(const vector<string> &dict_names)
    {
        _active_view.clear();
        for (const auto &name : dict_names)
        {
            auto it = _dict_words.find(name);
            if (it != _dict_words.end())
            {
                for (const auto &word : it->second)
                {
                    _active_view.push_back(&word);
                }
            }
        }
        // 排序（只排一次，视图排序，极快）
        sort(_active_view.begin(), _active_view.end(),
             [](const string *a, const string *b)
             { return *a < *b; });
    }

    // 3. 前缀搜索
    vector<string> prefix_search(const string &keyword, size_t limit)
    {
        vector<string> res;
        string key = keyword;
        for (const auto *word : _active_view)
        {
            if (res.size() >= limit)
                break;
            if (word->substr(0, key.size()) == key)
            {
                res.push_back(*word);
            }
        }
        return res;
    }

    // 4. 包含搜索
    vector<string> contains_search(const string &keyword, size_t limit)
    {
        vector<string> res;
        string key = to_lower(keyword);
        for (const auto *word : _active_view)
        {
            if (res.size() >= limit)
                break;
            if (to_lower(*word).find(key) != string::npos)
            {
                res.push_back(*word);
            }
        }
        return res;
    }

    // 5. 模糊搜索
    vector<string> fuzzy_search(const string &keyword, size_t limit)
    {
        string key = to_lower(keyword);
        priority_queue<pair<int, string>> heap;

        for (const auto *word : _active_view)
        {
            int d = levenshtein(key.c_str(), to_lower(*word).c_str());
            heap.emplace(-d, *word);
        }

        vector<string> res;
        while (!heap.empty() && res.size() < limit)
        {
            res.push_back(heap.top().second);
            heap.pop();
        }
        return res;
    }

    vector<string> fuzzy_contains_search(const string &keyword, size_t limit)
    {
        string key = to_lower(keyword);
        priority_queue<pair<int, string>> heap;

        for (const auto *word : _active_view)
        {
            if (to_lower(*word).find(key) != string::npos)
            {
                int d = levenshtein(key.c_str(), to_lower(*word).c_str());
                heap.emplace(-d, *word);
            }
        }

        vector<string> res;
        while (!heap.empty() && res.size() < limit)
        {
            res.push_back(heap.top().second);
            heap.pop();
        }
        return res;
    }
};

// ====================== 绑定 ======================
PYBIND11_MODULE(word_engine, m)
{
    py::class_<WordStorage>(m, "WordStorage")
        .def(py::init<>())
        .def("add_dict", &WordStorage::add_dict)
        .def("set_active_dicts", &WordStorage::set_active_dicts)
        .def("prefix_search", &WordStorage::prefix_search)
        .def("contains_search", &WordStorage::contains_search)
        .def("fuzzy_search", &WordStorage::fuzzy_search)
        .def("fuzzy_contains_search", &WordStorage::fuzzy_contains_search);
}