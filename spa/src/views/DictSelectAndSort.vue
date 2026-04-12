<template>
  <div ref="listRef" class="drag-list">
    <div v-for="item in list" :key="item.id" class="item">
      {{ item.name }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sortable from 'sortablejs'

const listRef = ref(null)
const list = ref([{ id:1, name:'1' }, { id:2, name:'2' }])

onMounted(() => {
  Sortable.create(listRef.value, {
    animation: 300,
    onEnd: ({ oldIndex, newIndex }) => {
      const item = list.value.splice(oldIndex, 1)[0]
      list.value.splice(newIndex, 0, item)
    }
  })
})
</script>