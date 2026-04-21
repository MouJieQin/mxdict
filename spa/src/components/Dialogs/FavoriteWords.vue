<template>
    <div>
        <el-table v-if="localFavoriteWords" :data="localFavoriteWords" height="350" style="width: 100%" stripe>
            <el-table-column fixed prop="word" label="Word" width="130" show-overflow-tooltip />
            <!-- <el-table-column fixed prop="created_at" label="Favorite At" width="130" show-overflow-tooltip /> -->
            <el-table-column fixed prop="query_count" label="Query Count" width="130" />
            <el-table-column fixed="right" label="Operations" width="130">
                <template #default="scope">
                    <el-button-group>
                        <el-button :icon="BsHeartbreak" size="small"
                            @click="handleUnFavorite(scope.$index, scope.row)" />
                        <el-button :icon="BsSearch" size="small" @click="handleSearch(scope.$index, scope.row)" />
                    </el-button-group>
                </template>
            </el-table-column>
        </el-table>
        <!-- make it show better -->
        Total: {{ localFavoriteWords.length }} words
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { PropType } from 'vue'
import { SessionWebSocketService } from '@/common/session-websocket-client'
import type { WordInfo, SessionConfig } from '@/common/type-interface'
import { BsHeartbreak, BsSearch } from 'vue-icons-plus/bs'

const props = defineProps({
    favoriteWordsDialogVisible: {
        type: Boolean,
        required: true
    },
    webSocket: {
        type: [SessionWebSocketService, null],
        required: true
    },
    favoriteWords: {
        type: Array as PropType<WordInfo[]>,
        required: true
    },
    sessionConfig: {
        type: Object as () => SessionConfig,
        required: true,
        default: () => ({})
    },
})

const emits = defineEmits<{
    (e: 'update-visible', visible: boolean): void
}>()

const localFavoriteWords = ref<WordInfo[]>([...props.favoriteWords])
watch(() => props.favoriteWords, (newVal) => {
    localFavoriteWords.value = [...newVal]
})

const handleUnFavorite = (_: number, row: WordInfo) => {
    props.webSocket?.sendToggleFavor(row.word, props.sessionConfig.default_folder.id)
}

const handleSearch = (_: number, row: WordInfo) => {
    props.webSocket?.sendLookupKeywordRequest(row.word)
    emits('update-visible', false)
}


</script>