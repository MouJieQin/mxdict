import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

// 懒加载组件
const Dict = () => import('@/views/DictPage.vue')

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        component: () => import('@/views/DictLayout.vue'),
        children: [
            {
                path: 'dict/:id',
                name: 'Dict',
                component: Dict
            }
        ]
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router  