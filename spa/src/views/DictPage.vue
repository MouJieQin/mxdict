<template>
    <Titlebar :webSocket="webSocket as SessionWebSocketService" :sessionId="sessionId"
        :isPinned="isFloatingWindowPinned" title="MXDict" :wordOptions="wordOptions" :redirectWord="redirectWord" />
    <div class="word-detail">
        <h1>음식</h1>
        <!-- <DictSelectAndSort /> -->
        <el-collapse expand-icon-position="left" v-model="activeNames">
            <div v-for="(result, dictName) in lookupKeywordResult" :key="dictName">
                <el-collapse-item :title="dictName" :name="dictName" :isActive="true">
                    <!-- {{ dictName }} -->
                    <div v-for="html in result" :key="html">
                        <el-divider />
                        <DictIframe :html="html" :css-url="dictInfo[dictName].css" :js-url="dictInfo[dictName].js"
                            :base-path="dictInfo[dictName].data" :dictionary-root="dictInfo[dictName].root"
                            @entry-click="handleEntryClick" />
                    </div>
                </el-collapse-item>
            </div>
        </el-collapse>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { SessionWebSocketService, useSessionWebSocket } from '@/common/session-websocket-client'
import Titlebar from '@/components/TitleBar/TitleBar.vue'
import DictSelectAndSort from '@/views/DictSelectAndSort.vue'


import DictIframe from '@/components/DictIframe.vue';


// 路由与状态
const route = useRoute()
const router = useRouter()

const webSocket = ref<SessionWebSocketService | null>(null)
// const bodyScrollTimeoutId = ref<number | null>(null)
const sessionId = ref(-1)
const redirectWord = ref<string>('')
const dictInfo = ref<any>(null)
const lookupKeywordResult = ref<any>(null)
const wordOptions = ref<string[]>([])

const activeNames = ref<string[]>([])
const isFloatingWindowPinned = ref(true) // 默认固定

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

// 处理WebSocket消息
const handleWebSocketMessage = (message: any) => {
    switch (message.type) {
        // case 'toggle_float_pin':
        //     handleToggleFloatPin(message)
        //     break
        case 'dict_info':
            dictInfo.value = message.data
            console.log('dict_info:', dictInfo.value)
            break
        case 'keyword_options_search':
            wordOptions.value = message.data.options
            console.log('keyword_options_search:', wordOptions.value)
            break
        case 'lookup_keyword':
            handleLookupKeyword(message.data)
            console.log('lookup_keyword:', message.data)
            break
        case 'toggle_floating_pin':
            isFloatingWindowPinned.value = message.data.is_pinned
            break
        case 'error_session_not_exist':
            router.push('/')
            break
    }
}

const handleLookupKeyword = (data: any) => {
    const keyword = data.keyword
    document.title = keyword || 'MxDict'
    lookupKeywordResult.value = data.result
    activeNames.value = Object.keys(data.result).map((key) => key)
    console.log('lookup_keyword', keyword, data)
}

const handleEntryClick = (entryPath: string) => {
    redirectWord.value = entryPath
    console.log('redirectWord.value:', redirectWord.value)
}



const handleScroll = () => {
    // autoHideScrollbar()
}

</script>