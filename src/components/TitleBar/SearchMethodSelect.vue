<template>
    <div class="icon-select-wrapper">
        <el-dropdown trigger="click" @command="handleSelect">
            <!-- 触发器：点击图标弹出 -->
            <span class="dropdown-trigger">
                <component :is="currentIcon" class="prefix-icon" />
            </span>

            <template #dropdown>
                <el-dropdown-menu>
                    <el-dropdown-item command="prefix_search">
                        <el-icon size="20">
                            <BsSearch />
                        </el-icon>
                        <span>前缀搜索</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="regex_search">
                        <el-icon size="20">
                            <VscRegex />
                        </el-icon>
                        <span>正则搜索</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="prefix_distance_search">
                        <el-icon size="20">
                            <Fa6Searchengin/>
                        </el-icon>
                        <span>前缀距离搜索</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="suggest_search">
                        <el-icon size="20">
                            <VscSearchFuzzy />
                        </el-icon>
                        <span>模糊搜索</span>
                    </el-dropdown-item>
                </el-dropdown-menu>
            </template>
        </el-dropdown>
    </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import {
    BsSearch,
} from 'vue-icons-plus/bs'
import { VscRegex, VscSearchFuzzy } from 'vue-icons-plus/vsc'
import { Fa6Searchengin } from 'vue-icons-plus/fa6'

const props = defineProps({
    searchMethod: {
        type: String,
        default: 'prefix_search',
    }
})

const emits = defineEmits<{
    (e: 'update-search-method', searchMethod: string): void
}>()

// 点击菜单项 → 触发更新
const handleSelect = (command: string) => {
    if (command !== props.searchMethod) {
        emits('update-search-method', command)
    }
}

// 动态切换图标
const currentIcon = computed(() => {
    const iconMap: Record<string, any> = {
        prefix_search: BsSearch,
        regex_search: VscRegex,
        prefix_distance_search: Fa6Searchengin,
        suggest_search: VscSearchFuzzy,
    }
    return iconMap[props.searchMethod] || BsSearch
})
</script>

<style scoped>
.dropdown-trigger {
    cursor: pointer;
    display: inline-flex;
    align-items: center;
}
</style>