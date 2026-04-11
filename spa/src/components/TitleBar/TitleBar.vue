<template>
    <!-- 自定义 macOS 标题栏（仅 macOS 显示，包含 Pin 置顶按钮） -->
    <div class="mxdict-titlebar">
        <div class="floating-window-titlebar">
            <el-autocomplete class="floating-window-search" v-model="keyword" :fetch-suggestions="querySearchAsync"
                placeholder="Please input" @select="handleSelect" ref="autoCompleteRef" @keyup.enter="handleEnter"
                @focus="handleFocus" clearable hide-loading />
        </div>
        <!-- <span class="floating-window-title">{{ title }}</span> -->
    </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted } from 'vue'
import { SessionWebSocketService } from '@/common/session-websocket-client'

const props = defineProps({
    webSocket: {
        type: [SessionWebSocketService, null],
        required: true
    },
    title: {
        type: String,
        required: true,
        default: 'Voichai'
    },
    wordOptions: {
        type: Array,
        default: () => [],
    },
    redirectWord: {
        type: String,
        required: true,
        default: '',
    },
})

const keyword = ref('')
// 定义与ref同名的变量
import type { ElAutocomplete } from 'element-plus'
const autoCompleteRef = ref<InstanceType<typeof ElAutocomplete> | null>(null)

// 用来存储定时器 ID（关键）
let searchTimer: number | null = null

// watch(() => keyword.value, (newVal) => {
// })

watch(() => props.wordOptions, () => {
    links.value = loadAll()
    isOptionsLoading.value = false
})

watch(() => props.redirectWord, (newVal) => {
    keyword.value = newVal
    lookupKeyword()
})



interface LinkItem {
    value: string
    link: string
}

const links = ref<LinkItem[]>([])

const loadAll = (): LinkItem[] => {
    return props.wordOptions.map(item => ({
        value: String(item),
        link: String(item),
    }))
}

let isOptionsLoading = ref(false)

const querySearchAsync = (queryString: string, cb: (arg: any) => void) => {
    console.log("queryString", queryString)
    if (!keyword.value.trim()) {
        return
    }
    isOptionsLoading.value = true
    props.webSocket?.sendKeywordOptionsSearch(keyword.value)

    // 1. 先清除上一次的定时器（核心！）
    if (searchTimer) {
        clearTimeout(searchTimer)
    }

    let timeCounter = 0
    searchTimer = setInterval(() => {
        timeCounter += 1
        if (timeCounter > 100) {
            isOptionsLoading.value = false
            cb(links.value)
            if (searchTimer) {
                clearTimeout(searchTimer)
            }
            return
        }
        console.log("waiting....")
        if (isOptionsLoading.value) {
            return
        }
        isOptionsLoading.value = false
        cb(links.value)
        console.log("links.value", links.value)
        if (searchTimer) {
            clearTimeout(searchTimer)
        }
    }, 50)
}

const lookupKeyword = () => {
    props.webSocket?.sendLookupKeyword(keyword.value)
}

const handleEnter = (e: KeyboardEvent) => {
    e.preventDefault()
    lookupKeyword();
    (autoCompleteRef.value as InstanceType<typeof ElAutocomplete> | null)?.close()

    console.log("handleEnter:", keyword.value)
}

const handleSelect = (item: Record<string, any>) => {
    lookupKeyword()
    console.log("handleSelect:", item.value)
}

const handleFocus = (e: FocusEvent) => {
    // 拿到原生 input 元素并全选
    (e.target as HTMLInputElement).select()
}


onMounted(() => {
    links.value = loadAll()
})

</script>
