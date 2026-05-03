<template>
  <div ref="listRef" class="dict-select-sort-dialog">
    <div class="dict-settings-drag-cards" v-for="item in list" :key="item.id">
      <el-card class="dict-settings-drag-card" shadow="always" :class="{ 'is-disabled': !item.is_enabled }">
        <div class="dict-settings-drag-card-content">
          <div class="left-group">
            <el-image :src="item.cover_url" class="icon">
              <template #error>
                <BiSolidBookBookmark size="35" />
              </template>
            </el-image>
            <span class="name">{{ item.name }}</span>
          </div>
          <div class="right-group">
            <el-switch v-model="item.is_enabled" />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Sortable from 'sortablejs'

import type { DictSettingInfo, DictsSettingInfo, SessionConfig } from '@/common/type-interface'
import type { PropType } from 'vue'
import { BiSolidBookBookmark } from 'vue-icons-plus/bi'
import { SessionWebSocketService } from '@/common/session-websocket-client'

const props = defineProps({
  dictSSDialogVisible: {
    type: Boolean,
    require: true
  },
  webSocket: {
    type: [SessionWebSocketService, null],
    required: true
  },
  sessionConfig: {
    type: Object as PropType<SessionConfig>,
    required: true
  }
})

const listRef = ref(null)
const sessionConfig = ref<SessionConfig>(JSON.parse(JSON.stringify(props.sessionConfig || {})))
const list = ref<DictsSettingInfo>(sessionConfig.value?.dictsSettingInfo || [])

watch(() => props.dictSSDialogVisible, (newVal) => {
  if (newVal) {
    sessionConfig.value = JSON.parse(JSON.stringify(props.sessionConfig || {}))
    list.value = sessionConfig.value?.dictsSettingInfo || []
  } else {
    if (JSON.stringify(sessionConfig.value) !== JSON.stringify(props.sessionConfig)) {
      props.webSocket?.sendSessionConfig(sessionConfig.value)
    }
  }
})

onMounted(() => {
  Sortable.create(listRef.value as unknown as HTMLElement, {
    animation: 300,
    onEnd: ({ oldIndex, newIndex }) => {
      const item = list.value?.splice(oldIndex as number, 1)[0]
      list.value?.splice(newIndex as number, 0, item as DictSettingInfo)
      console.log('New list order:', list.value?.map(i => i.name).join(', '))
    }
  })
})
</script>
