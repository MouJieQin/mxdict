<template>
    <Titlebar :webSocket="webSocket as SessionWebSocketService" :sessionId="sessionId"
        :isWordFavorited="isWordFavorited" :sessionConfig="sessionConfig as SessionConfig"
        :favoriteWords="favoriteWords" :searchHistory="searchHistory" :isPinned="isFloatingWindowPinned"
        :lastSearchKeyword="lastSearchKeyword" :hasResultLastSearch="hasResultLastSearch" :noteContent="noteContent"
        :wordOptions="wordOptions" :redirectWord="redirectWord" @change:keyword="handleChangeKeyword" />
    <div class="word-detail">
        <el-collapse expand-icon-position="left" v-model="activeNames">
            <el-collapse-item v-if="noteContent" title="我的笔记" name="我的笔记" :isActive="true">
                <el-divider style="margin:0 10px" />
                <!-- 음식 -->
                <div v-html="md.render(noteContent)"></div>
            </el-collapse-item>
            <div v-for="(result, dictName) in lookupKeywordResult" :key="dictName">
                <el-collapse-item :title="dictName" :name="dictName" :isActive="true"
                    style="font-weight:bold !important;">
                    <div v-for="html in result" :key="html">
                        <el-divider style="margin:0 10px" />
                        <DictIframe :html="html" :css-urls="dictsInfo[dictName].css" :js-urls="dictsInfo[dictName].js"
                            :base-path="dictsInfo[dictName].data" :dictionary-root="dictsInfo[dictName].root"
                            @entry-click="handleEntryClick" />
                    </div>
                </el-collapse-item>
            </div>
        </el-collapse>
        <div v-show="!keyword && !hasResultLastSearch">
            <p class="dict-homepage-type-p">Type a word to look up in…</p>
            <br />
            <div v-for="dictSetting in sessionConfig.dictsSettingInfo" :key="dictSetting.id">
                <p class="dict-homepage-dict-p" v-show="dictSetting.is_enabled">{{
                    dictSetting.name }}</p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { SessionWebSocketService, useSessionWebSocket } from '@/common/session-websocket-client'
import Titlebar from '@/components/TitleBar/TitleBar.vue'
import DictIframe from '@/components/DictIframe.vue';
import type { DictsInfo, SessionConfig, WordInfo, WordInfoWithLastSearch } from '@/common/type-interface'
import { useSystemConfigStore } from '@/stores/stores'
import MarkdownIt from 'markdown-it'
const md = new MarkdownIt()


// 路由与状态
const route = useRoute()
const router = useRouter()

const systemConfigStore = useSystemConfigStore()
const webSocket = ref<SessionWebSocketService | null>(null)
// const bodyScrollTimeoutId = ref<number | null>(null)
const keyword = ref('')
const sessionId = ref(-1)
const redirectWord = ref<string>('')
const dictsInfo = ref<DictsInfo>({})
const sessionConfig = ref<SessionConfig>({
    default_folder: { "id": null },
    dictsSettingInfo: [],
    default_search_method: { "method": "prefix_search" }
})
const lookupKeywordResult = ref<any>(null)
const wordOptions = ref<string[]>([])

const activeNames = ref<string[]>([])
const isWordFavorited = ref<boolean>(false)
const isFloatingWindowPinned = ref(true) // 默认固定
const lastSearchKeyword = ref<string>('')
const noteContent = ref<string>('')
const hasResultLastSearch = ref<boolean>(false)
const favoriteWords = ref<WordInfo[]>([])
const searchHistory = ref<WordInfoWithLastSearch[]>([])


const setupDicsSettingsInfo = () => {
    if (!sessionConfig.value?.dictsSettingInfo) {
        for (const dictName in dictsInfo.value) {
            const dict = dictsInfo.value[dictName]
            sessionConfig.value?.dictsSettingInfo.push({
                id: dictName,
                name: dict.name,
                cover_url: `http://localhost:5959/api/download?path=${dict.cover}`,
                is_enabled: true
            })
        }
    } else {
        for (const dictName in dictsInfo.value) {
            const dict = dictsInfo.value[dictName]
            const dictSetting = sessionConfig.value?.dictsSettingInfo.find(item => item.id === dictName)
            if (!dictSetting) {
                sessionConfig.value?.dictsSettingInfo.push({
                    id: dictName,
                    name: dict.name,
                    cover_url: `http://localhost:5959/api/download?path=${dict.cover}`,
                    is_enabled: true
                })
            }
        }
    }
}

// 初始化WebSocket
const setupWebSocket = () => {
    sessionId.value = Number(route.params.id)
    webSocket.value = useSessionWebSocket(sessionId.value)
    if (webSocket.value) {
        webSocket.value.handleMessage = (message: any) => {
            handleWebSocketMessage(message)
        }
    }
}

// 初始化
onMounted(() => {
    setupWebSocket()
    // window.addEventListener('keydown', handleKeydown)
    window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
    // 移除滚动事件监听器，防止内存泄漏
    window.removeEventListener('scroll', handleScroll)
})

router.beforeEach(async (__, _, next) => {
    // 关闭 WebSocket
    webSocket.value?.close()
    next()
})

onBeforeUnmount(() => {
    document.title = 'MxDict'
})

const handleChangeKeyword = (newKeyword: string) => {
    keyword.value = newKeyword
}


// 处理WebSocket消息
const handleWebSocketMessage = (message: any) => {
    switch (message.type) {
        // case 'toggle_float_pin':
        //     handleToggleFloatPin(message)
        //     break
        case 'dict_info':
            dictsInfo.value = message.data
            setupDicsSettingsInfo()
            console.log('dict_info:', dictsInfo.value)
            break
        case 'keyword_options_search':
            wordOptions.value = message.data.options
            console.log('keyword_options_search:', wordOptions.value)
            break
        case 'lookup_keyword_request':
            redirectWord.value = message.data.keyword
            console.log('lookup_keyword_request:', message.data)
            break
        case 'word_note':
            noteContent.value = message.data.note || ''
            break
        case 'lookup_keyword':
            handleLookupKeyword(message.data)
            console.log('lookup_keyword:', message.data)
            break
        case 'session_config':
            sessionConfig.value = message.data.config
            console.log('session_config:', sessionConfig.value)
            break
        case 'toggle_floating_pin':
            isFloatingWindowPinned.value = message.data.is_pinned
            break
        case 'toggle_favor':
            console.log('toggle_favor:', message.data)
            handleToggleFavor(message.data)
            break
        case 'favorite_words':
            favoriteWords.value = message.data.words
            console.log('favorite_words:', favoriteWords.value)
            break
        case 'search_history':
            searchHistory.value = message.data.words
            console.log('search_history:', searchHistory.value)
            break
        case 'system_config':
            systemConfigStore.setSystemConfig(message.data)
            console.log('system_config:', message.data)
            break
        case 'error_session_not_exist':
            router.push('/')
            break
    }
}

const handleLookupKeyword = (data: any) => {
    const keyword = data.keyword
    document.title = keyword || 'MxDict'
    lastSearchKeyword.value = keyword || ''
    noteContent.value = data.note || ''
    lookupKeywordResult.value = data.result
    hasResultLastSearch.value = data.result !== null && data.result !== undefined && Object.keys(data.result).length !== 0
    console.log('Object.keys(data.result).length:', Object.keys(data.result).length)
    isWordFavorited.value = data.is_word_favorited
    activeNames.value = Object.keys(data.result).map((key) => key)
    activeNames.value.push('我的笔记')
    console.log('lookup_keyword', keyword, data)
}

const handleEntryClick = (entryPath: string) => {
    redirectWord.value = entryPath
    console.log('redirectWord.value:', redirectWord.value)
}

const handleToggleFavor = (data: any) => {

    isWordFavorited.value = data.is_word_favorited
    // add  word if it is not in favoriteWords.value or delete the word in favoriteWords.value
    if (!isWordFavorited.value) {
        favoriteWords.value = favoriteWords.value.filter((item: WordInfo) => item.word !== data.keyword)
    }
}

const handleScroll = () => {
    // autoHideScrollbar()
}

</script>