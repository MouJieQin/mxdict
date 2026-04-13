<template>
    <!-- 自定义 macOS 标题栏（仅 macOS 显示，包含 Pin 置顶按钮） -->
    <div class="mxdict-titlebar">
        <div class="floating-window-titlebar">
            <div class="floating-window-search-container">
                <el-autocomplete class="floating-window-search" v-model="keyword" :fetch-suggestions="querySearchAsync"
                    placeholder="Search" @select="handleSelect" ref="autoCompleteRef" @keyup.enter="handleEnter"
                    @focus="handleFocus" clearable hide-loading>
                    <!-- 前缀插槽：动态图标 + 点击弹出下拉 -->
                    <template #prefix>
                        <SearchMethodSelect :searchMethod="searchMethod"
                            @update-search-method="handleSearchMethodChange" />
                    </template>
                </el-autocomplete>
            </div>
            <el-button-group class="floating-window-titlebar-button-container">
                <el-button :icon="ImBooks" text @click="dictSSDialogVisible = !dictSSDialogVisible"
                    class="floating-window-titlebar-button" size="small" />
                <el-button :icon="props.isPinned ? BsPinAngleFill : BsPin" text @click="handlePinClick"
                    class="floating-window-titlebar-button" size="small" />
            </el-button-group>
        </div>
        <el-dialog v-model="dictSSDialogVisible" fullscreen>
            <DictSelectAndSortDialog :webSocket="props.webSocket" :dictSSDialogVisible="dictSSDialogVisible"
                :dictsSetting="props.dictsSetting"></DictSelectAndSortDialog>
        </el-dialog>
    </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted } from 'vue'
import { SessionWebSocketService } from '@/common/session-websocket-client'
import {
    BsPin, BsPinAngleFill,
} from 'vue-icons-plus/bs'
import { ImBooks } from 'vue-icons-plus/im'
import SearchMethodSelect from '@/components/TitleBar/SearchMethodSelect.vue'
import DictSelectAndSortDialog from '@/components/Dialogs/DictSelectAndSortDialog.vue'
import { type DictsSettingInfo } from '@/common/type-interface'



const props = defineProps({
    webSocket: {
        type: [SessionWebSocketService, null],
        required: true
    },
    sessionId: {
        type: Number,
        required: true
    },
    dictsSetting: {
        type: Array as () => DictsSettingInfo,
        default: () => []
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
    isPinned: {
        type: Boolean,
        default: true
    }
})

const keyword = ref('')
const searchMethod = ref('prefix_search') // 默认搜索方法
const dictSSDialogVisible = ref(false)
// 定义与ref同名的变量
import type { ElAutocomplete } from 'element-plus'
const autoCompleteRef = ref<InstanceType<typeof ElAutocomplete> | null>(null)

// 用来存储定时器 ID（关键）
let searchTimer: number | null = null

const handlePinClick = () => {
    props.webSocket?.sendFloatingWindowPinClick(props.sessionId)
}

const handleSearchMethodChange = (newMethod: string) => {
    searchMethod.value = newMethod
    // 重新触发搜索以应用新的搜索方法
    if (keyword.value.trim()) {
        querySearchAsync(keyword.value, () => { })
    }
}

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

const getDictSettingsForLookup = () => {
    // return a list that contains the dict name which is not disable in the same order.
    let dictnames: string[] = []
    props.dictsSetting.filter(item => item.is_enabled).map(item => dictnames.push(item.name))
    return dictnames
}

const querySearchAsync = (queryString: string, cb: (arg: any) => void) => {
    console.log("queryString", queryString)
    if (!keyword.value.trim()) {
        return
    }
    isOptionsLoading.value = true
    props.webSocket?.sendKeywordOptionsSearch(keyword.value, searchMethod.value, getDictSettingsForLookup())

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
    props.webSocket?.sendLookupKeyword(keyword.value, getDictSettingsForLookup())
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
