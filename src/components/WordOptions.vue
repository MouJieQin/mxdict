<template>
    <!-- UseVirtualList handles all virtual scrolling logic out of the box -->
    <UseVirtualList :list="wordOptions" :options="{ itemHeight: 30, overscan: 20 }" height="calc(100% + 40px)"
        class="list-container">
        <!-- VueUse reliably passes 'data' and 'index' for raw strings -->
        <template #default="{ data, index }">
            <div class="item-content clickable-row" :style="{ height: '30px' }" @click="handleWordClick(data)">
                <el-text>row {{ index }} - {{ data }}</el-text>
            </div>
        </template>
    </UseVirtualList>
</template>

<script lang="ts" setup>
import { UseVirtualList } from '@vueuse/components'
import { SessionWebSocketService } from '@/common/session-websocket-client'

const props = withDefaults(
    defineProps<{
        webSocket: SessionWebSocketService | null
        wordOptions?: string[] // Back to your original, clean string array!
    }>(),
    {
        wordOptions: () => []
    }
)

const handleWordClick = (word: string) => {
    console.log('Selected word:', word)
    props.webSocket?.sendLookupKeywordRequest(word)
}
</script>

<style scoped>
.list-container {
    border: 1px solid var(--el-border-color-light, #e4e7ed);
    border-radius: 4px;
}

.clickable-row {
    display: flex;
    align-items: center;
    padding: 0 16px;
    box-sizing: border-box;
    cursor: pointer;
    border-bottom: 1px solid var(--el-border-color-extra-light, #f2f6fc);
    transition: background-color 0.2s ease;
}

.clickable-row:hover {
    background-color: var(--el-fill-color-light, #f5f7fa);
}
</style>
