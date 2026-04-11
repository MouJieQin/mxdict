<template>
    <Titlebar :webSocket="webSocket" title="MXDict" :wordOptions="wordOptions" :redirectWord="redirectWord" />
    <div class="word-detail">
        <h1>음식</h1>
        <!-- <el-collapse expand-icon-position="left"> -->
        <div v-for="(result, dictName) in lookupKeywordResult" :key="dictName">
            <!-- <el-collapse-item :title="dictName" :name="dictName" :isActive="true"> -->
            {{ dictName }}
            <div v-for="html in result" :key="html">
                <el-divider />
                <DictIframe :html="html" :css-url="dictInfo[dictName].css" :js-url="dictInfo[dictName].js"
                    :base-path="dictInfo[dictName].data" :dictionary-root="dictInfo[dictName].root"
                    @entry-click="handleEntryClick" />
            </div>
            <!-- </el-collapse-item> -->
            <!-- </el-collapse> -->
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import { SessionWebSocketService, useSessionWebSocket } from '@/common/session-websocket-client'
import Titlebar from '@/components/TitleBar/TitleBar.vue'

import DictIframe from '@/components/DictIframe.vue';


// 路由与状态
const route = useRoute()
const router = useRouter()

const webSocket = ref<SessionWebSocketService | null>(null)
const bodyScrollTimeoutId = ref<number | null>(null)
const sessionId = ref(-1)
let redirectWord = ref<string>('')
let dictInfo = ref<any>(null)
let lookupKeywordResult = ref<any>(null)
let wordOptions = ref<string[]>([])

// 监听路由变化
const watchRouteChange = () => {
    watch(() => route.params.id, (newId) => {
        const newSessionId = newId ? Number(newId) : -1
        if (newSessionId !== sessionId.value) {
            sessionId.value = newSessionId
            setupWebSocket()
        }
    }, { immediate: true })
}

// 初始化WebSocket
const setupWebSocket = () => {
    webSocket.value = useSessionWebSocket(sessionId.value)
    if (webSocket.value) {
        webSocket.value.handleMessage = (message: any) => {
            handleWebSocketMessage(message)
        }
    }
}

// 初始化
onMounted(() => {
    watchRouteChange()
    // setupWebSocket()
    // window.addEventListener('keydown', handleKeydown)
    window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
    // 移除滚动事件监听器，防止内存泄漏
    window.removeEventListener('scroll', handleScroll)
})

router.beforeEach(async (to, from, next) => {
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
        case 'error_session_not_exist':
            router.push('/')
            break
    }
}

const handleLookupKeyword = (data: any) => {
    const keyword = data.keyword
    document.title = keyword || 'MxDict'
    lookupKeywordResult.value = data.result
    console.log('lookup_keyword', keyword, data)
}

const handleEntryClick = (entryPath: string) => {
    redirectWord.value = entryPath
    console.log('redirectWord.value:', redirectWord.value)
}


const autoHideScrollbar = () => {
    if (bodyScrollTimeoutId.value) {
        clearTimeout(bodyScrollTimeoutId.value)
    }
    const scrollbarBackground = getComputedStyle(document.documentElement)
        .getPropertyValue('--scrollbar-background');
    document.documentElement.style.setProperty('--body-scrollbar-background', scrollbarBackground)
    bodyScrollTimeoutId.value = setTimeout(() => {
        document.documentElement.style.setProperty('--body-scrollbar-background', 'rgba(0, 0, 0, 0)')
        bodyScrollTimeoutId.value = null
    }, 1000)
}

const handleScroll = () => {
    // autoHideScrollbar()
}

</script>