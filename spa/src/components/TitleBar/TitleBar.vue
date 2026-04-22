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
                <el-tooltip v-if="showFavorButtonTooltip" content="请先设置默认收藏夹" trigger="hover">
                    <el-button :icon="BsHeart" text class="floating-window-titlebar-button" size="small" disabled />
                </el-tooltip>
                <el-button v-if="!showFavorButtonTooltip" :icon="props.isWordFavorited ? BsHeartFill : BsHeart" text
                    @click="handleFavorClick" class="floating-window-titlebar-button" size="small"
                    :disabled="!(lastSearchKeyword !== '' && props.hasResultLastSearch)" />

                <el-button :icon="Edit" text @click="noteDialogVisible = true"
                    class="floating-window-titlebar-button" size="small"
                    :disabled="!(lastSearchKeyword !== '')" />

                <el-button :icon="ImBooks" text @click="dictSSDialogVisible = !dictSSDialogVisible"
                    class="floating-window-titlebar-button" size="small" id="titlebar-dictss-button" />
                <el-button :icon="Setting" text id="titlebar-setting-button"
                    @click="settingDialogVisible = !settingDialogVisible" class="floating-window-titlebar-button"
                    size="small" />
                <el-button :icon="props.isPinned ? BsPinAngleFill : BsPin" text @click="handlePinClick"
                    class="floating-window-titlebar-button" size="small" />
            </el-button-group>
        </div>

        <el-dialog v-model="noteDialogVisible" :title="'「' + lastSearchKeyword + '」' + '的笔记'" width="500" align-center>
            <el-input v-model="noteContent" autocomplete="off" type="textarea" :autosize="{ minRows: 5, maxRows: 9 }" />
            <template #footer>
                <div class="dialog-footer">
                    <el-popconfirm confirm-button-text="删除" confirm-button-type="danger" cancel-button-text="取消"
                        :icon="Delete" icon-color="#FF4949" title="确定删除笔记吗？" @confirm="handleDeleteNote">
                        <template #reference>
                            <el-button :icon="Delete" type="danger">Delete</el-button>
                        </template>
                    </el-popconfirm>

                    <el-button @click="noteDialogVisible = false">Cancel</el-button>
                    <el-button type="primary" @click="submitNote">
                        Confirm
                    </el-button>
                </div>
            </template>
        </el-dialog>

        <el-dialog v-model="favoriteWordsDialogVisible" fullscreen>
            <FavoriteWords :favoriteWordsDialogVisible="favoriteWordsDialogVisible" :webSocket="props.webSocket"
                @update-visible="(visible) => favoriteWordsDialogVisible = visible" :favoriteWords="props.favoriteWords"
                :sessionConfig="props.sessionConfig" />
        </el-dialog>
        <el-dialog v-model="settingDialogVisible" fullscreen>
            <Settings :webSocket="props.webSocket" :settingDialogVisible="settingDialogVisible"
                :sessionConfig="props.sessionConfig"></Settings>
        </el-dialog>
        <el-dialog v-model="dictSSDialogVisible" fullscreen>
            <DictSelectAndSortDialog :webSocket="props.webSocket" :dictSSDialogVisible="dictSSDialogVisible"
                :sessionConfig="props.sessionConfig"></DictSelectAndSortDialog>
        </el-dialog>
    </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted, computed, onBeforeUnmount } from 'vue'
import type { PropType } from 'vue'
import { SessionWebSocketService } from '@/common/session-websocket-client'
import {
    BsPin, BsPinAngleFill, BsHeartFill, BsHeart,
} from 'vue-icons-plus/bs'
import { ImBooks } from 'vue-icons-plus/im'
import SearchMethodSelect from '@/components/TitleBar/SearchMethodSelect.vue'
import DictSelectAndSortDialog from '@/components/Dialogs/DictSelectAndSortDialog.vue'
import Settings from '@/views/Settings.vue'
import FavoriteWords from '@/components/Dialogs/FavoriteWords.vue'
import { type SessionConfig } from '@/common/type-interface'
import { getDictSettingsForLookup } from '@/common/utility'
import { Setting, Edit, Delete } from '@element-plus/icons-vue'
import { useSystemConfigStore } from '@/stores/stores'
import type { WordInfo } from '@/common/type-interface'


const props = defineProps({
    webSocket: {
        type: [SessionWebSocketService, null],
        required: true
    },
    sessionId: {
        type: Number,
        required: true
    },
    sessionConfig: {
        type: Object as () => SessionConfig,
        required: true,
        default: () => ({})
    },
    favoriteWords: {
        type: Array as PropType<WordInfo[]>,
        required: true,
        default: () => [],
    },
    lastSearchKeyword: {
        type: String,
        required: true,
    },
    hasResultLastSearch: {
        type: Boolean,
        required: true,
        default: false,
    },
    noteContent: {
        type: String,
        required: true,
        default: '',
    },
    isWordFavorited: {
        type: Boolean,
        required: true,
        default: false,
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
const favoriteWordsDialogVisible = ref(false)
const dictSSDialogVisible = ref(false)
const settingDialogVisible = ref(false)
// 定义与ref同名的变量
import type { ElAutocomplete } from 'element-plus'
import { before } from 'node:test'
const autoCompleteRef = ref<InstanceType<typeof ElAutocomplete> | null>(null)
const systemConfigStore = useSystemConfigStore()
const noteDialogVisible = ref(false)
const noteContent = ref(props.noteContent)



const handleDeleteNote = () => {
    props.webSocket?.sendDeleteWordNote(props.lastSearchKeyword)
    noteDialogVisible.value = false
}

const submitNote = () => {
    if (!noteContent.value.trim()) {
        return
    }
    props.webSocket?.sendSaveWordNote(props.lastSearchKeyword, noteContent.value)
    noteDialogVisible.value = false
}

watch(() => props.noteContent, (newVal) => {
    noteContent.value = newVal
})

watch(() => favoriteWordsDialogVisible.value, (newVal) => {
    if (newVal) {
        props.webSocket?.sendFavoriteWordsRequest()
    }
})


// 用来存储定时器 ID（关键）
let searchTimer: number | null = null


const showFavorButtonTooltip = computed(() => {
    return !props.sessionConfig.default_folder.id || !systemConfigStore.systemConfig?.folders?.folder_info.some((item) => item.id === props.sessionConfig.default_folder.id)
})

const handlePinClick = () => {
    props.webSocket?.sendFloatingWindowPinClick(props.sessionId)
}

const handleFavorClick = () => {
    props.webSocket?.sendToggleFavor(props.lastSearchKeyword, props.sessionConfig.default_folder.id)
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

const querySearchAsync = (queryString: string, cb: (arg: any) => void) => {
    console.log("queryString", queryString)
    if (!keyword.value.trim()) {
        return
    }
    isOptionsLoading.value = true
    props.webSocket?.sendKeywordOptionsSearch(keyword.value, searchMethod.value, getDictSettingsForLookup(props.sessionConfig.dictsSettingInfo || []))

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
    props.webSocket?.sendLookupKeyword(keyword.value.trim(), props.sessionConfig.default_folder.id, getDictSettingsForLookup(props.sessionConfig.dictsSettingInfo || []))
}

const handleEnter = (e: KeyboardEvent) => {
    e.preventDefault()
    if (props.lastSearchKeyword === keyword.value.trim()) {
        return
    }
    lookupKeyword();
    (autoCompleteRef.value as InstanceType<typeof ElAutocomplete> | null)?.close()
}

const handleSelect = (item: Record<string, any>) => {
    lookupKeyword()
    console.log("handleSelect:", item.value)
}

const handleFocus = (e: FocusEvent) => {
    // 拿到原生 input 元素并全选
    (e.target as HTMLInputElement).select()
}

const handleKeydown = (e: KeyboardEvent) => {
    if (e.key === '/' && e.metaKey) {
        e.preventDefault();
        favoriteWordsDialogVisible.value = !favoriteWordsDialogVisible.value;
        return;
    }
}


onMounted(() => {
    links.value = loadAll()
    window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeydown)
})

</script>
