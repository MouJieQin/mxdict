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

import type { DictSettingInfo, DictsSettingInfo } from '@/common/type-interface'
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
  dictsSetting: {
    type: Object as PropType<DictsSettingInfo>,
    required: true
  }
})

const listRef = ref(null)
const list = ref<DictsSettingInfo>(JSON.parse(JSON.stringify(props.dictsSetting)))

watch(() => props.dictSSDialogVisible, (newVal) => {
  if (newVal) {
    list.value = JSON.parse(JSON.stringify(props.dictsSetting))
  } else {
    if (JSON.stringify(list.value) !== JSON.stringify(props.dictsSetting)) {
      props.webSocket?.sendSessionDictSettings(list.value as DictsSettingInfo)
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
