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
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

import { SessionWebSocketService, useSessionWebSocket } from '@/common/session-websocket-client'
import Titlebar from '@/components/TitleBar/TitleBar.vue'

import DictIframe from '@/components/DictIframe.vue';


// 路由与状态
const router = useRouter()

const webSocket = ref<SessionWebSocketService | null>(null)
let redirectWord = ref<string>('')
let dictInfo = ref<any>(null)
let lookupKeywordResult = ref<any>(null)
let wordOptions = ref<string[]>([])

// 初始化WebSocket
const setupWebSocket = () => {
    webSocket.value = useSessionWebSocket()
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
})


router.beforeEach(async (to, from, next) => {
    // 关闭 WebSocket
    webSocket.value?.close()
    next()
})

onBeforeUnmount(() => {
    document.title = 'MXDict'

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
</script>